# baseAdmin

A framework for administrative applications, consisting of a web-based UI and REST backend interface.

## Rationale

Having developed several solutions that included an administrative backend, common patterns emerged. With baseAdmin I'm extracting the common parts into a framework that can be forked and extended for specific applications. The main goal is a have a working solution out of the box that can be extended with minimal (redundant) effort.

## Philosophy

The main goal of baseAdmin is out of the box functionality that is extendable with minimal effort. Therefore it is highly driven by conventions. Trying to break away from these conventions will result in pain. If you feel that any of the conventions don't fit your needs, you better don't use baseAdmin.

## Technology Stack

baseAdmin uses the following technology:

* Backend
  * Python with Flask and Flask_Restful
  * Mongo DB
* Frontend
  * Bootstrap
  * Vue.js

## How to Use baseAdmin

1. Fork this repository
2. (optional, but likely) Rename your repository
3. Deploy your fork to Heroku  
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)  
(You now have your very own working baseAdmin installation, running the demo application.)
4. Clone your fork and start implementing your own application on top of baseAdmin.
5. (optional, but advised) Add the initial baseAdmin repository as an upstream remote:  
`git remote add upstream https://github.com/christophevg/baseAdmin`
6. Update your baseAdmin framework:  
`git fetch upstream; git checkout master; git merge upstream/master`  
(Hint: The top-level `Makefile` contains a target to do this: `make update`)

> The `backend` folder is part of the baseAdmin repository, but act as placeholders for implementing your own application. Most files will never be part of commits to baseAdmin and can be edited and committed to just for your application. Future changes to baseAdmin will be mergeable onto your repository and will reuse your changes. Exception to this rule of thumb is: `__init__.py`, which sets up the environment and provides the following objects to work with: `app`, `mongo` and `api`, as well as an `authenticate` decorator.
They initially contain the demo applicationm, which you can use to start your own application from.

## Running baseAdmin Locally

The first time only: create a virtual Python environment:

```bash
$ virtualenv venv
```

From then on, activate the virtual environment, update it and run your backend:

```bash
$ . venv/bin/activate
(venv) $ pip install -r requirements.txt
(venv) $ python run.py
```
