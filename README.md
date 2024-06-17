<p align="center">
  <picture>
    <img src="ckanext/iepnb/public/img/iepnb-logo.png" style="height:100px">
  </picture>
</p>
<h1 align="center">ckanext-iepnb - Theming customisation</h1>
<p align="center">
<a href="https://github.com/OpenDataGIS/ckanext-iepnb/actions/workflows/test.yml"><img src="https://github.com/OpenDataGIS/ckanext-iepnb/actions/workflows/test.yml/badge.svg?branch=main&event=pull_request" alt="ckanext-iepnb tests"></a>

<p align="center">
    <a href="#overview">Overview</a> •
    <a href="#requirements">Requirements</a> •
    <a href="#improvements">Improvements</a> •
    <a href="#installation">Installation</a> •
    <a href="#harvesters">Harvesters</a> •
    <a href="#config-settings">Config settings</a> •
    <a href="#developer-installation">Developer installation</a> •
    <a href="#tests">Tests</a> •
    <a href="#releasing-a-new-version-of-ckanext-iepnb">Release</a> •
    <a href="#license">License</a>
</p>

## Overview
`ckanext-iepnb` is a customisation of CKAN to be used as an IEPNB extension, sharing styles, images and other assets with the [main site](https://iepnb.es) and merging with it on the same server.

> [!IMPORTANT]
>This is a **custom extension** with specific theme for the [IEPNB](https://www.miteco.gob.es/es/biodiversidad/temas/inventarios-nacionales/inventario-espanol-patrimonio-natural-biodiv.html). Use with: [`ckan-docker-iepnb`](https://github.com/OpenDataGIS/ckan-docker-iepnb) 


## Requirements
Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.8             | not tested    |
| 2.9             | yes           |
| 2.10            | not tested    |


`ckanext-iepnb` needs the following extensions:

* [`mjanez/ckanext-dcat`](https://github.com/mjanez/ckanext-dcat):
  ````bash
  pip install -e git+https://github.com/mjanez/ckanext-dcat.git@v1.6.0#egg=ckanext-dcat
  pip install -r ./src/ckanext-dcat/requirements.txt
  ````

* [`ckanext-scheming`](https://github.com/ckan/ckanext-scheming):
  ```bash
  pip install -e git+https://github.com/ckan/ckanext-scheming.git@release-3.0.0#egg=ckanext-scheming
  pip install -r ./src/ckanext-schemingdcat/requirements.txt
  ```

* [`ckanext-spatial`](https://github.com/ckan/ckanext-spatial):
  ```bash
  pip install -e git+https://github.com/ckan/ckanext-spatial.git@v2.1.1#egg=ckanext-spatial
  pip install -r ./src/ckanext-spatial/requirements.txt
  ```

* [`mjanez/ckanext-schemingdcat`](https://github.com/mjanez/ckanext-schemingdcat):
  ```bash
  pip install -e git+https://github.com/mjanez/ckanext-schemingdcat.git@v3.0.0#egg=ckanext_schemingdcat
  pip install -r ./src/ckanext-schemingdcat/requirements.txt
  ```

* [`opendatagis/ckanext-sparql_interface`](https://github.com/OpenDataGIS/ckanext-sparql_interface):
  ```bash
  pip install -e git+https://github.com/OpenDataGIS/ckanext-sparql_interface.git@2.0.2-iepnb#egg=ckanext-sparql_interface
  pip install -r ./src/ckanext-sparql_interface/requirements.txt
  ```

And modify `ckan.ini`, You can use the default values:
 ```ini
 ckan.plugins = "... sparql_interface spatial_metadata spatial_query resource_proxy geo_view geojson_view wmts_view shp_view dcat schemingdcat_datasets schemingdcat_groups schemingdcat_organizations iepnb schemingdcat"

# ckanext-dcat (dcat.base_uri = CKAN instance URL)
ckanext.dcat.base_uri = https://.iepnb.es/catalogo
ckanext.dcat.rdf.profiles = euro_dcat_ap_2
ckanext.dcat.default_catalog_endpoint = /catalog.{_format}

 # ckanext-scheming
scheming.dataset_schemas = "ckanext.schemingdcat:schemas/geodcatap_es/geodcatap_es_dataset.yaml"
scheming.group_schemas = "ckanext.schemingdcat:schemas/geodcatap_es/geodcatap_es_group.json"
scheming.organization_schemas = "ckanext.schemingdcat:schemas/geodcatap_es/geodcatap_es_org.json"
scheming.presets = "ckanext.schemingdcat:schemas/default_presets.json ckanext.fluent:presets.json"

# ckanext-spatial (Solr Backend - solr8-spatial)
ckanext.spatial.search_backend = solr-bbox
ckan.spatial.srid = 3857
ckanext.spatial.common_map.type = custom
ckanext.spatial.common_map.custom_url = https://rts.larioja.org/mapa-base/rioja/{z}/{x}/{y}.png
ckanext.spatial.common_map.attribution = "Map tiles by <a href=\"http://openstreetmap.org\">OpenStreetMap</a> (<a href=\"http://creativecommons.org/licenses/by-sa/3.0\">CC BY SA</a>)"

# ckanext-geoview
ckanext.geoview.geojson.max_file_size = 1024
ckanext.geoview.ol_viewer.formats = "wms wfs geojson gml kml"
ckanext.geoview.shp_viewer.srid = 3857
ckanext.geoview.shp_viewer.encoding = UTF-8

### ckanext-schemingdcat
schemingdcat.facet_list = "tags groups theme theme_es dcat_type groups spatial_uri owner_org res_format frequency tag_uri conforms_to"
schemingdcat.organization_custom_facets = True
schemingdcat.group_custom_facets = True
schemingdcat.geometadata_base_uri = https://.iepnb.es/csw

# ckanext-sparql_interface
ckanext.sparql.endpoint_url = https://datos.iepnb.es/sparql
ckanext.sparql.hide_endpoint_url=False

 ```

## Improvements
`ckanext-iepnb` tries to merge the CKAN and IEPNB styles, it might be good if the values used in the CSS directives were stored in CSS variables, so that `ckanext-iepnb` could call them to override CKAN, and changes made by the design team without having to rewrite them in the extension.

Since header and footer are the blocks shared between CKAN and the rest of the iepnb site, perhaps it would be a good improvement to wrap them in a class that allows iepnb styles to take precedence over CKAN styles in these blocks. This could be further improved by having the styles that affect those blocks in their own css files, separate from the styles that affect the main block or the page as a whole.

This extension displays a summary of various metadata elements in the left column.

## Installation

To install `ckanext-iepnb`:

1. Activate your CKAN virtual environment, for example:

    ```bash
    `. /usr/lib/ckan/default/bin/activate`
    ```

2. Clone the source and install it on the virtualenv

    ```bash
    git clone https://github.com/OpenDataGIS/ckanext-iepnb.git
    cd ckanext-iepnb
    pip install -e .
	  pip install -r requirements.txt
    ```

3. Add `iepnb` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).
   		
4. Add `iepnb` specific configuration to the CKAN config file

5. Restart CKAN.

>[!TIP]
> If CKAN does not start, try making the directory `/ckan/ckan/public/base/i18n` writable by the ckan user.


## Harvesters
### Basic using
In production, when `gather` and `consumer` processes are running, the following command are used to start and stop the background processes:

  - `ckan harvester run`: Starts any harvest jobs that have been created by putting them onto
    the gather queue. Also checks running jobs - if finished it
    changes their status to Finished.

To testing harvesters in development, you can use the following command:
  - `ckan harvester run-test {source-id/name}`: This does all the stages of the harvest (creates job, gather, fetch, import) without involving the web UI or the queue backends. This is useful for testing a harvester without having to fire up gather/fetch_consumer processes, as is done in production.

    > [!WARNING]
    > After running the `run-test` command, you should stop all background processes for `gather` and `consumer` to avoid conflicts.

### Remote Google Sheet/Onedrive Excel metadata upload Harvester - IEPNB
A harvester for remote Excel files with Metadata records. This harvester is a subclass of the Scheming DCAT Base Harvester provided by `ckanext-schemingdcat` to provide a more versatile and customizable harvester for Excel files that have metadata records in them.

To use it, you need to add the `iepnb_harvester` plugin to your options file:

  ```ini
  ckan.plugins = harvest schemingdcat schemingdcat_datasets iepnb ... iepnb_harvester
  ```

Remote Google Sheet/Onedrive Excel metadata upload Harvester supports the options described in the [`ckanext-schemingdcat harvester`](https://github.com/mjanez/ckanext-schemingdcat?tab=readme-ov-file#remote-google-sheetonedrive-excel-metadata-upload-harvester)

**Example**
Here are some examples of configuration files:

* *Field positions*: With `field_position` to define the mapping based on positions of attributes in the remote sheet (`A`, `B`, `AA`, etc.).
  ```json
  {
    "storage_type": "gspread",
    "dataset_sheet": "Dataset",
    "distribution_sheet": "Distribution",

    ...
    # other properties
    ...

    "field_mapping_schema_version": 2,
    "dataset_field_mapping": {
      "title": {
          "field_position": "A"
        },
      "title_translated": {
          "languages": {
              "en": {
                  "field_position": "AC"
              },
              "de": {
                  "field_value": ""
              },
              "es": {
                  "field_position": "A"
              }
          }
      },
      "private": {
          "field_position": "F"
      },
      "theme": {
          "field_position": ["G", "AA"],
      },
      "tag_custom": {
          "field_position": "B"
      },
      "tag_string": {
          "field_position": ["A", "B", "AC"]
      },
      "theme_es": {
          "field_value": "http://datos.gob.es/kos/sector-publico/sector/medio-ambiente"
      },
      "tag_uri": {
          "field_position": "Z",
          // "field_value" extends the original list of values retrieved from the remote file for all records.
          "field_value": ["https://www.example.org/codelist/a","https://www.example.org/codelist/b", "https://www.example.org/codelist/c"] 
      },
    }
  }
  ```

  * *Field names*: With `field_name` to define the mapping based on names of attributes in the remote sheet (`my_title`, `org_identifier`, `keywords`).

  ```json
  {
    "storage_type": "gspread",
    "dataset_sheet": "Dataset",
    "distribution_sheet": "Distribution",

    ...
    # other properties
    ...

    "field_mapping_schema_version": 2,
    "dataset_field_mapping": {
      "title": {
          "field_name": "my_title"
        },
      "title_translated": {
          "languages": {
              "en": {
                  "field_name": "my_title-en"
              },
              "de": {
                  "field_value": ""
              },
              "es": {
                  "field_name": "my_title"
              }
          }
      },
      "private": {
          "field_name": "private"
      },
      "theme": {
          "field_name": ["theme", "theme_eu"]
      },
      "tag_custom": {
          "field_name": "keywords"
      },
      "tag_string": {
          "field_name": ["theme_a", "theme_b", "theme_c"]
      },
      "theme_es": {
          "field_value": "http://datos.gob.es/kos/sector-publico/sector/medio-ambiente"
      },
      "tag_uri": {
          "field_name": "keyword_uri",
          // "field_value" extends the original list of values retrieved from the remote file for all records.
          "field_value": ["https://www.example.org/codelist/a","https://www.example.org/codelist/b", "https://www.example.org/codelist/c"] 
      },
    }
  }
  ```

>[!IMPORTANT]
> All `*_translated` fields need their fallback `non-suffix` field as simple field, e.g: 
> ```json
> ...
>    "title": {
>         "field_position": "A"
>      },
>    "title_translated": {
>        "languages": {
>            "en": {
>                "field_value": ""
>            },
>            "es": {
>                "field_position": "A"
>            }
>       }
>    },
> ...
>```

## Config settings
At CKAN config .ini file (in `/etc/ckan/default` dir), into the [app:main] 
section, add:

```ini
#Server to download menu and breadcrumbs. Demo assets server: https://github.com/OpenDataGIS/ckanext-iepnb_assets
iepnb.server = https://iepnb.es

#default breadcrumbs
iepnb.breadcrumbs = [{"title":"Some literal","description":"Some description", "relative":"relative_path_from_iepnb.server"},...]
#example: iepnb.breadcrumbs = [{"title":"Nuestros datos","description":"Nuestros datos", "relative":"/nuestros-datos"},{"title":"Catálogo de datos","description":"Catálogo de datos", "relative":"/catalogo"}]


#relative path to download menu in iepnb.server. Demo path_menu in ckanext-iepnb_assets: /main.json
iepnb.path_menu = /apis/menu_items/main         

#number of popular tags to show at index page
iepnb.popular_tags = 6

#relative path to download breadcrumbs definition. Will take precedence over iepnb.headcrumbs if defined
iepnb.path_breadcrumbs = '[{"title":"Nuestros datos","description":"Nuestros datos", "relative":"/nuestros-datos"},{"title":"Catálogo de datos","description":"Catálogo de datos", "relative":"/catalogo"}]'
	
```

And in order to replace the default ckan favicon with the desired, change the appropriate key:

```ini
ckan.favicon=/base/images/iepnb.ico
```

breadcrumbs are shown in the same order that are defined in the key's value

### Stats configuration
Having stats on is a bit tricky. First of all you must have the plugin 
activated at the `ckan.plugins` setting in the config .ini file. usually you 
have it out-of-the-box, so it's not a big deal. Since you have it enabled, 
you'll get a "Stats menu" option under the "Stats" section in the main page 
when logged as a ckan user.

Ok. That was the easy part. Unfortunately, even thoug stats plugin is part of 
the ckan core, it is a little outdated in ckan 2.9, and it doesn't work. In 
order to have stats enabled you must edit `index.html` template in 
`ckanext/stats/templates/ckanext/stats`, and change all the references to the 
"c" object to access its properties directly. So for example you must replace 
`c.largest_groups` by just `largest_groups` (without the 'c.' part).

This is just a patch for ckan versions shipped with an outdated 'stats' 
plugin, so you must first test if the plugin works (just accessing the main 
menu option and checking the stats), and only then apply the proposed patch (if 
the plugin doesn't works).

## Developer installation
To install ckanext-iepnb for development, activate your CKAN virtualenv and
do:

```bash
git clone https://github.com/OpenDataGIS/ckanext-iepnb.git
cd ckanext-iepnb
python setup.py develop
pip install -r dev-requirements.txt
```

## Tests
Be sure that ckan user has write rights in the root dir of the extension 
(perhaps ckanext-iepnb?). If that is not the case and if for security or other 
reasons you can't do it, create a .pytest_cache dir at the root dir of the
extension and make it writable by the ckan user.

To run the tests, at `ckanext-iepnb` root dir do:

```bash
pip install -r dev-requirements.txt
pytest --ckan-ini=test.ini
```

To have a more verbose test, you can do:

```bash
pytest -vv --ckan-ini=test.ini`
```

This will give you a few deprecation warnings. You can ignore those about
code outside the extension. Ckan needs a very specific versions of the python
libs it uses, so please do not mess upgrading libs in order to supress the
warnings. Just ignore them.

## Releasing a new version of ckanext-iepnb
If ckanext-iepnb should be available on PyPI you can follow these steps to 
publish a new version:

1. Update the version number in the `setup.py` file. See 
   [PEP 440](http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers) 
   for how to choose version numbers.

2. Make sure you have the latest version of necessary packages:

	  ```bash
      pip install --upgrade setuptools wheel twine
      ```

3. Create a source and binary distributions of the new version:

	  ```bash
      python setup.py sdist bdist_wheel && twine check dist/*
      ```

   Fix any errors you get.

4. Upload the source distribution to PyPI:

	  ```bash
      twine upload dist/*
      ```

5. Commit any outstanding changes:

	  ```bash
      git commit -a
	  git push
      ```

6. Tag the new release of the project on GitHub with the version number from
   the `setup.py` file. For example if the version number in `setup.py` is
   0.0.1 then do:
   
	```bash
	  git tag 0.0.1
	  git push --tags
	```

## License
[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
