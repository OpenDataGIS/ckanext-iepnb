# CKAN-IEPNB - Customization

ckan-iepnb is a customization of ckan to use it as a iepnb extension, sharing styles, images and other assets with the main site, merging with it in the same server

Honor and praise to the developer of this extension: <a href="mailto:dsanjurj@tragsa.es">**dsanjurj@tragsa.es**</a>

Contact him if **you** do something wrong and mistakenly believe is a code issue

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.8             | not tested    |
| 2.9             | yes           |
| 2.10            | not tested    |

Suggested values:

* "yes"
* "not tested" - I can't think of a reason why it wouldn't work
* "not yet" - there is an intention to get it working
* "no"

## Improvements

As ckan-iepnb tries a merge between ckan and iepnb styles, it could be fine if 
the values used in css directives were stored in css variables, so ckan-iepnb 
could recall them to overwrite ckan styles, and changes made by the design 
team could be visibles without need of rewrite them in the extension.

Since header and footer are the block shared between ckan and the rest of the
iepnb site, perhaps it could be a good improvement to enclose them in a class
which lets iepnb styles take precedence over ckan ones into those blocks. This
could be improved further having the styles affecting those blocks in its own
css files, separated from the styles that affect the main block or the page as 
a whole.

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
   
4. In order to let the English profile work, is absolutely mandatory to make 
   the directory `/ckan/ckan/public/base/i18n` writable by the ckan user. 
   ¡CKAN WILL NOT START IF YOU DON'T DO SO!
		
5. Add iepnb specific configuration to the CKAN config file

6. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     `sudo service apache2 reload`
     


## Config settings

At CKAN config .ini file (in `/etc/ckan/default` dir), into the [app:main] 
section, add:

```ini
#Server to download menu and breadcrumbs. Demo assets server: https://github.com/OpenDataGIS/ckanext-iepnb_assets
iepnb.server = https://some_server

#default breadcrumbs
iepnb.breadcrumbs = [{"title":"Some literal","description":"Some description", "relative":"relative_path_from_iepnb.server"},...]
#example: iepnb.breadcrumbs = [{"title":"Nuestros datos","description":"Nuestros datos", "relative":"/nuestros-datos"},{"title":"Catálogo de datos","description":"Catálogo de datos", "relative":"/catalogo"}]


#relative path to download menu in iepnb.server. Demo path_menu in ckanext-iepnb_assets: /main.json
iepnb.path_menu = /api/menu_items/main         

#number of popular tags to show at index page
iepnb.popular_tags = 3

#relative path to download breadcrumbs definition. Will take precedence over iepnb.headcrumbs if defined
iepnb.path_breadcrumbs = No_Default_Value
	
```

And in order to replace the default ckan favicon with the desired, change the appropriate key:

```ini
ckan.favicon=/base/images/iepnb.ico
```

breadcrumbs are shown in the same order that are defined in the key's value

###Stats configuration

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
git clone https://github.com/TRAGSATEC/ckanext-iepnb.git
cd ckanext-iepnb
python setup.py develop
pip install -r dev-requirements.txt
```

## Tests

To run the tests, do:

`pytest --ckan-ini=test.ini` (not implemented yet) 


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
