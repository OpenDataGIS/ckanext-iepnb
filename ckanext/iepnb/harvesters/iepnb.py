
import logging
from urllib.parse import urlparse
import mimetypes
import requests
import re
import pandas as pd

from ckan.plugins.core import SingletonPlugin, implements

from ckanext.schemingdcat.harvesters.base import RemoteResourceError
from ckanext.schemingdcat.interfaces import ISchemingDCATHarvester
import ckanext.schemingdcat.helpers as sdct_helpers
from ckanext.iepnb.config import IEPNB_HARVESTER_MD_CONFIG, IEPNB_PUBLISHER_TYPES

from ckanext.schemingdcat.config import (
    COMMON_DATE_FORMATS,
    mimetype_base_uri,
    URL_FIELD_NAMES,
    EMAIL_FIELD_NAMES,
    OGC2CKAN_MD_FORMATS,
)

log = logging.getLogger(__name__)


# TODO: IEPNB Harvester
class IEPNBHarvester(SingletonPlugin):
    '''
    An enhanced bulk metadata upload harvester for IEPNB.
    '''
    _field_choices = None
    _default_lang = 'es'

    implements(ISchemingDCATHarvester)

    def before_cleaning(self, content_dicts, harvest_job, harvester_config=None):
        """
        Before cleaning the content_dicts, this function checks if the dataset_sheet and distribution_sheet, specified in the configuration, are the same.
        If they are, it adds a 'dataset_id' column to both the 'datasets' and 'distributions' dataframes in the content_dicts.
        The 'dataset_id' is identical for both and is constructed as 'id_{index}'.

        Args:
            content_dicts (dict): The downloaded content_dicts, which contains the 'datasets' and 'distributions' dataframes.
            harvest_job (HarvestJob): The current harvest job.

        Returns:
            tuple: A tuple containing the updated content_dicts and an empty list.
        """
        log.debug('In IEPNBHarvester before_cleaning')
        error_msg = []

        try:
            dataset_sheetname = harvester_config.get("dataset_sheet")
            distribution_sheetname = harvester_config.get("distribution_sheet")

            if dataset_sheetname == distribution_sheetname:
                # Ensure that 'content_dicts' is a dictionary containing the dataframes
                if isinstance(content_dicts, dict) and 'datasets' in content_dicts and 'distributions' in content_dicts:
                    df_datasets = content_dicts['datasets']
                    df_distributions = content_dicts['distributions']

                    # Check if 'identifier' column exists in df_datasets
                    if 'identifier' in df_datasets.columns:
                        # Use 'identifier' from df_datasets as 'dataset_id' in df_distributions
                        df_distributions['dataset_id'] = df_datasets['identifier']
                    else:
                        # Create the 'identifier' column and assign an identical id
                        df_datasets['identifier'] = ['id_%s' % i for i in range(len(df_datasets))]
                        df_distributions['dataset_id'] = ['id_%s' % i for i in range(len(df_distributions))]

                    # If 'url' and 'format' columns in df_distributions contain comma-separated lists or single strings, handle them appropriately
                    df_distributions = self._process_distributions(df_distributions)

                    # Strip leading and trailing whitespace from 'url' column
                    df_distributions['url'] = df_distributions['url'].str.strip()

                    # Update the content_dicts with the new dataframes
                    content_dicts['datasets'] = df_datasets
                    content_dicts['distributions'] = df_distributions

        except RemoteResourceError as e:
            error_msg.append("IEPNBHarvester-before_cleaning: Error during processing harvest url <%s>: %s" % (harvest_job.source.url, e))
            log.error("IEPNBHarvester-before_cleaning: Error during processing harvest url <%s>: %s", harvest_job.source.url, e)
            return content_dicts, error_msg

        return content_dicts, error_msg

    def after_cleaning(self, clean_datasets):
        """
        This method is called after the cleaning process of the datasets. It removes the 'identifier' field from each dataset.

        Args:
            clean_datasets (list): A list of cleaned datasets.

        Returns:
            tuple: A tuple containing the list of cleaned datasets with the 'identifier' field removed and an empty list.

        Raises:
            Exception: If there is an error while removing the 'identifier' field from a dataset.
        """
        log.debug('In IEPNBHarvester after_cleaning')
        error_msg = []

        for dataset in clean_datasets:
            try:
                dataset.pop('identifier', None)
            except RemoteResourceError as e:
                error_msg.append("IEPNBHarvester-after_cleaning: Error removing 'identifier' field: %s" % e)
                log.error("IEPNBHarvester-after_cleaning: Error removing 'identifier' field: %s", e)
                return clean_datasets, error_msg

        log.info("IEPNBHarvester-after_cleaning: Temporary field 'identifier' has been removed from datasets")

        return clean_datasets, error_msg
    
    # Adapt datasets for IEPNB
    def before_create(self, harvest_object, package_dict, local_schema, harvester_tmp_dict):
        log.debug('In IEPNBHarvester before_create')
        return self._process_package(harvest_object, package_dict, local_schema, harvester_tmp_dict)

    def before_update(self, harvest_object, package_dict, local_schema, harvester_tmp_dict):
        log.debug('In IEPNBHarvester before_update')
        return self._process_package(harvest_object, package_dict, local_schema, harvester_tmp_dict)
    
    @classmethod
    def _process_package(self, harvest_object, package_dict, local_schema, harvester_tmp_dict):
        err = None
        
        self._set_field_choices(local_schema)
        
        # Update URLs
        self._update_urls(package_dict)
        
        # Mapping label values from choices to correct values
        self._get_values_from_choices(package_dict, 'es')

        # Convert private field to boolean
        if 'private' in package_dict:
            package_dict['private'] = package_dict['private'].lower() == 'true'      

        # Set default notes
        if (
            'notes_translated' not in package_dict or 
            not package_dict['notes_translated'] or 
            self._default_lang not in package_dict['notes_translated'] or 
            not package_dict['notes_translated'][self._default_lang]
        ):
            package_dict['notes_translated'] = IEPNB_HARVESTER_MD_CONFIG["notes_translated"][self._default_lang]

        # Check default contact/publisher info
        package_dict = self._check_contact_publisher_info(package_dict)

        # Normalize reference_system
        if 'reference_system' in package_dict:
            package_dict['reference_system'] = self._transform_reference_system(package_dict['reference_system'])

        # Normalize fields that should be URLs and emails
        package_dict = self._normalize_url_fields(package_dict)
        package_dict = self._normalize_email_fields(package_dict)

        # Improve distributions, with format etc.
        for resource in package_dict['resources']:
            
            # If URL is None or "" url = ""
            if resource['url'] is None:
                resource['url'] = ""
            
            # Try to infer the EPSG
            resource['reference_system'] = package_dict.get('reference_system', None)

            # Set availability=avalaible as default
            resource['availability'] = IEPNB_HARVESTER_MD_CONFIG["resources"]["availability"]

            # Try to generate default name
            resource_name = IEPNB_HARVESTER_MD_CONFIG["resources"]["name"][self._default_lang].format(format=resource['format'].upper()) if resource.get('format') else None
            resource['name'] = resource_name if resource_name else resource.get('name', '')
                
        #log.debug('package_dict: %s', package_dict)
        
        return err

    @staticmethod
    def _process_distributions(df_distributions):
        """
        Process the distributions DataFrame to handle 'url' and 'format' columns.

        This method takes a DataFrame of distributions and processes the 'url' and 'format' columns.
        If 'url' column contains strings separated by comma, they are split into separate rows.
        If 'url' column does not contain comma but contains newline, they are split into separate rows.
        If 'url' column does not contain either comma or newline, it is treated as a single URL.
        Each new row is a copy of the original row, with 'url' replaced by one of the split values.
        If 'format' column exists and contains strings separated by comma or newline, they are split and assigned to the new rows.
        If the number of 'url' and 'format' values doesn't match, 'format' is set to None.

        Args:
            df_distributions (pandas.DataFrame): The DataFrame of distributions to process.

        Returns:
            pandas.DataFrame: The processed DataFrame of distributions.
        """        
        new_rows = []
        for _, row in df_distributions.iterrows():
            urls = row['url'].split(',') if ',' in row['url'] else row['url'].splitlines() if '\n' in row['url'] else [row['url']]
            formats = row.get('format', '').split(',') if ',' in row.get('format', '') else row.get('format', '').splitlines() if '\n' in row.get('format', '') else [row.get('format', '')]

            if len(urls) != len(formats):
                formats = [None] * len(urls)

            new_rows.extend([dict(row, url=url.strip() if url else url, format=format.strip() if format else format) for url, format in zip(urls, formats)])

        df_distributions = pd.DataFrame(new_rows)

        return df_distributions

    @classmethod
    def _set_field_choices(self, local_schema, default_lang='es'):
        if self._field_choices is None:
            self._field_choices = {}
            for f in local_schema['dataset_fields']:
                if 'choices' in f:
                    field_name = f['field_name']
                    choices = f['choices']
                    self._field_choices[field_name] = {
                        choice['label'][default_lang].lower().strip(): choice['value']
                        for choice in choices if isinstance(choice['label'], dict) and default_lang in choice['label']
                    }    

    @classmethod
    def _get_values_from_choices(self, package_dict, default_lang='es'):
        """
        Processes the values in the package_dict based on the field choices defined in the local schema.
        Also applies the same logic to the resources in the package_dict if they exist.
        Returns the updated package_dict.

        Args:
            package_dict (dict): The package dictionary to process.
            default_lang (str, optional): The default language. Defaults to 'es'.

        Returns:
            dict: The processed package dictionary.
        """
        def process_value(value, field_name):
            if isinstance(value, list):
                return [self._field_choices[field_name].get(val.lower().strip(), val) for val in value]
            else:
                processed_value = value.lower().strip()
                return self._field_choices[field_name].get(processed_value, value)

        def process_dict(data_dict):
            for field_name, value in data_dict.items():
                if value is not None and field_name in self._field_choices:
                    data_dict[field_name] = process_value(value, field_name)
            return data_dict

        package_dict = process_dict(package_dict)

        if "resources" in package_dict:
            package_dict["resources"] = [process_dict(resource) for resource in package_dict["resources"]]

        return package_dict

    @staticmethod
    def _update_urls(package_dict, url_fields=None):
        """
        Update URL fields in the package dictionary to ensure they start with 'http://' or 'https://'.

        If a URL field does not start with 'http://' or 'https://', 'https://' is prepended to it.

        Args:
            package_dict (dict): The package dictionary where URL fields are to be updated.
            url_fields (list, optional): A list of URL fields to be updated. Defaults to ['author_url', 'contact_url', 'publisher_url', 'maintainer_url'].

        Returns:
            dict: The updated package dictionary.
        """
        if url_fields is None:
            url_fields = ['author_url', 'contact_url', 'publisher_url', 'maintainer_url']

        for field in url_fields:
            url = package_dict.get(field)
            if url:
                parsed_url = urlparse(url)
                package_dict[field] = url if parsed_url.scheme else 'https://' + url

        return package_dict

    @staticmethod
    def _normalize_url_fields(package_dict):
        """
        Normalize URL fields in the package dictionary.

        Args:
            package_dict (dict): The package dictionary to normalize.
        """
        # List of fields that should be updated to the default value
        default_fields = ['publisher_url', 'contact_url', 'spatial_uri']

        # Normalize URL fields in dataset
        for field in URL_FIELD_NAMES['dataset']:
            if field in package_dict:
                if isinstance(package_dict[field], list):
                    # The field is a list, iterate over its elements
                    for i, url in enumerate(package_dict[field]):
                        if not sdct_helpers.schemingdcat_check_valid_url(url):
                            package_dict[field][i] = IEPNB_HARVESTER_MD_CONFIG.get(field, None) if field in default_fields else None
                else:
                    # The field is not a list, check the URL directly
                    if not sdct_helpers.schemingdcat_check_valid_url(package_dict[field]):
                        # The field isn't a valid URL, assign default value if it exists, otherwise None
                        package_dict[field] = IEPNB_HARVESTER_MD_CONFIG.get(field, None) if field in default_fields else None

        # Normalize URL fields in resources
        if "resources" in package_dict:
            for resource in package_dict["resources"]:
                for field in URL_FIELD_NAMES['resource']:
                    if field in resource:
                        if not sdct_helpers.schemingdcat_check_valid_url(resource[field]):
                            # The URL isn't valid, assign default value if it exists, otherwise None
                            resource[field] = IEPNB_HARVESTER_MD_CONFIG.get(field, None) if field in default_fields else None
                            
        return package_dict
            
    @staticmethod                    
    def _normalize_email_fields(package_dict):
        """
        Normalize email fields in the package dictionary.

        Args:
            package_dict (dict): The package dictionary to normalize.
        """
        # List of fields that should not be updated to the default value
        default_fields = ['publisher_email', 'contact_email']

        # Normalize email fields
        for field in EMAIL_FIELD_NAMES:
            if field in package_dict:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", package_dict[field]):
                    # The field isn't a valid email, assign default value if it exists and the field is not in no_default_fields, otherwise None
                    package_dict[field] = IEPNB_HARVESTER_MD_CONFIG.get(field, None) if field in default_fields else None
                    
        return package_dict

    @staticmethod
    def _transform_reference_system(reference_system):
        """
        Transform a reference_system string into the correct URI.

        If the reference_system is a string in the format "EPSG:<code> <description>", it is transformed into
        the format "http://www.opengis.net/def/crs/EPSG/0/<code>". If the reference_system is already a URI, it is left unchanged.

        Args:
            reference_system (str): The reference_system string to transform.

        Returns:
            str: The transformed reference_system string.
        """
        # Regular expression to match "EPSG:<code>"
        pattern = r"EPSG:(\d+)"

        # If the reference_system matches the pattern, transform it into the correct URI
        match = re.search(pattern, reference_system)
        if match:
            code = match.group(1)
            return f"http://www.opengis.net/def/crs/EPSG/0/{code}"

        # If the reference_system doesn't match the pattern, return None
        return None

    @staticmethod
    def _check_contact_publisher_info(package_dict):
        """
        Check and update 'contact' and 'publisher' fields in a data dictionary.

        If 'contact_name' or 'publisher_name' fields are None, all corresponding 'contact_*' or 'publisher_*' fields are updated with default values from IEPNB_HARVESTER_MD_CONFIG. If a default value does not exist, None is assigned.

        Args:
            data_dict (dict): The data dictionary to check and update.

        Returns:
            dict: The updated data dictionary.
        """

        contact_fields = [
            'contact_name',
            'contact_email',
            'contact_uri',
            'contact_url'
        ]

        publisher_fields = [
            'publisher_name',
            'publisher_identifier',
            'publisher_uri',
            'publisher_email',
            'publisher_url',
            'publisher_type'
        ]        

        if package_dict.get('contact_name') is None:
            for field in contact_fields:
                package_dict[field] = IEPNB_HARVESTER_MD_CONFIG[field]

        if package_dict.get('publisher_name') is None:
            for field in publisher_fields:
                package_dict[field] = IEPNB_HARVESTER_MD_CONFIG[field]
        else:
            publisher_name_lower = package_dict.get('publisher_name', '').lower()
            for publisher_type in IEPNB_PUBLISHER_TYPES.values():
                if publisher_type['label'] in publisher_name_lower:
                    package_dict['publisher_type'] = publisher_type['value']
                    break

        return package_dict