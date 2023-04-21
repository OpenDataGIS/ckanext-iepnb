# CKAN-IEPNB - Customization

ckan-iepnb is a customization of ckan to use it as a iepnb extension, sharing styles, images and other assets with the main site, merging with it in the same server

Honor and praise to the developer of this extension: <a href="mailto:dsanjurj@tragsa.es">**dsanjurj@tragsa.es**</a>

Contact him if **you** do something wrong and mistakenly believe is a code issue

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.6 and earlier | not tested    |
| 2.7             | not tested    |
| 2.8             | not tested    |
| 2.9             | yes    |

Suggested values:

* "yes"
* "not tested" - I can't think of a reason why it wouldn't work
* "not yet" - there is an intention to get it working
* "no"

## Improvements

As ckan-iepnb tries a merge between ckan and iepnb styles, it could be fine if the values used in css directives were stored in css variables, so ckan-iepnb could recall them to overwrite ckan directives, and changes made by the design team could be visibles without need of rewrite them in the extension.

## Installation

To install ckanext-iepnb:

1. Activate your CKAN virtual environment, for example:

     `. /usr/lib/ckan/default/bin/activate`

2. Clone the source and install it on the virtualenv

    ```
    git clone https://github.com/OpenDataGIS/ckanext-iepnb.git
    cd ckanext-iepnb
    pip install -e .
	pip install -r requirements.txt
    ```

3. Add `iepnb` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).
   
4. Clear the index in solr:

	`ckan -c [route to your .ini ckan config file] search-index clear`
   
5. Modify the schema file on Solr (schema or managed schema) to add the multivalued fields added in the scheming extension used for faceting:

	
```xml
	<! IEPNB extra fields - >
    <field name="tag_uri" type="string" uninvertible="false" docValues="true" indexed="true" stored="true" multiValued="true"/>
    <field name="conforms_to" type="string" uninvertible="false" docValues="true" indexed="true" stored="true" multiValued="true"/>
    <field name="lineage_source" type="string" uninvertible="false" docValues="true" indexed="true" stored="true" multiValued="true"/>
    <field name="lineage_process_step" type="string" uninvertible="false" docValues="true" indexed="true" stored="true" multiValued="true"/>
    <field name="reference" type="string" uninvertible="false" docValues="true" indexed="true" stored="true" multiValued="true"/>
    <field name="theme" type="string" uninvertible="false" docValues="true" indexed="true" stored="true" multiValued="true"/>
    <field name="resource_relation" type="string" uninvertible="false" docValues="true" indexed="true" stored="true" multiValued="true"/>
	
```
   	
	Be sure to restart Solr after modify the schema
		
6. Add iepnb specific configuration to the CKAN config file

7. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     `sudo service apache2 reload`
     
8. Reindex solr index:

	`ckan -c [route to your .ini ckan config file] search-index rebuild`

	Sometimes solr can issue an error while reindexing. In that case I´d try to restart solr, delete index ("search-index clear"), restart solr, rebuild index, and restart solr again.


## Config settings

At CKAN config .ini file (in `/etc/ckan/default` dir), into the [app:main] section, add:

```
	#Server to download menu and breadcrumbs. Demo assets server: https://github.com/OpenDataGIS/ckanext-iepnb_assets
	iepnb.server = https://some_server

	#default breadcrumbs
	iepnb.breadcrumbs = [{"title":"Some literal","description":"Some description", "relative":"relative_path_from_iepnb.server"},...]

	#relative path to download menu in iepnb.server. Demo path_menu in ckanext-iepnb_assets: /main.json
	iepnb.path_menu = /api/menu_items/main         

	#number of popular tags to show at index page
	iepnb.popular_tags = 3

	#relative path to download breadcrumbs definition. Will take precedence over iepnb.headcrumbs if defined
	iepnb.path_breadcrumbs = No_Default_Value
	
	#list of facets to show in search page, and its order. This options are just an example, you can select your own
	iepnb.facet_list = theme theme_es dcat_type owner_org res_format publisher_name publisher_type frequency tags tag_uri conforms_to
```	

## Developer installation

To install ckanext-iepnb for development, activate your CKAN virtualenv and
do:

```bash
git clone https://github.com/TRAGSATEC/ckanext-iepnb.git
cd ckanext-iepnb
python setup.py develop
pip install -r dev-requirements.txt
```

## Icons management

This extension made automatic use of icons for fields defined in the schema file and using uris as values.

To be this extension able to use the icons they must be stored acording these rules:

* Icons for items must be in a subdirectory of public/images/icons, named after the field name.
* For each item, its icon must be in a directory inside the named before, this named as the second-to-last fragment in the value´s path, and the file named as the last fragment of this value.
* All names in lowercase letters
* Icons can have svg, png, jpg or gif extensions.

Examples:

field_name: theme

* value: http://inspire.ec.europa.eu/theme/mf1
  * icon -> public/images/icons/theme/theme/mf1.svg (the repeated 'theme' is not a mistake)

field_name: spatial

* value: http://datos.gob.es/recurso/sector-publico/territorio/Autonomia/Aragon
  * icon -> public/images/icons/autonomia/aragon.svg
  
* value: http://datos.gob.es/recurso/sector-publico/territorio/Pais/España
  * icon -> public/images/icons/pais/españa (note the lowercases and keep an eye on non-ascii-128 character translations between systems)

To take advantage of the automatic use of icons, two display_snippets are provided in templates/scheming/display_snipets:

* select_icon.html: to be used with one-select fields
* multiple_choice_icon.html: to be used with multiple-select fields

You can use these snippets configuring the display_snippet property in your scheming file as appropiate.  

## Tests

To run the tests, do:

`pytest --ckan-ini=test.ini` (not implemented yet) 


## Releasing a new version of ckanext-iepnb

If ckanext-iepnb should be available on PyPI you can follow these steps to publish a new version:

1. Update the version number in the `setup.py` file. See [PEP 440](http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers) for how to choose version numbers.

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
