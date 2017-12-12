# baseAdmin

A framework for administrative applications, consisting of a web-based UI and REST backend interface.

## Work in Progress Warning ;-)

I've only just started working on this, so until this warning is removed, I wouldn't trust myself using this ;-) Do play with it, but things can still change overnight.

## Rationale

Having developed several solutions that included an administrative backend, common patterns emerged. With baseAdmin I'm extracting the common parts into a framework that can be forked and extended for specific applications. The main goal is a have a working solution out of the box that can be extended with minimal (redundant) effort.

## Philosophy

The main goal of baseAdmin is out of the box functionality that is extendable with minimal effort. Therefore it is highly driven by conventions. Trying to break away from these conventions will result in pain. If you feel that any of the conventions don't fit your needs, you better don't use baseAdmin.

## Technology Stack

This project stands on the shoulders of these wonderful high-power projects:

* Backend
  * Python
  * [Flask](http://flask.pocoo.org)
  * [Flask_Restful](http://flask-restful.readthedocs.io/en/latest/)
  * Mongo DB
* Frontend
  * [Vue.js](https://vuejs.org)
  * [Vuex](https://vuex.vuejs.org)
  * [Vuetify](https://vuetifyjs.com)
  * [Vue ChartJS](http://vue-chartjs.org)

## How to Use baseAdmin

1. Fork this repository
2. (optional, but likely) Rename your repository
3. Deploy your fork to Heroku  
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)  
You now have your very own working baseAdmin installation, running the demo application. The latest version of this repository is continuously deployed to [https://baseadmin-demo.herokuapp.com](https://baseadmin-demo.herokuapp.com).
4. Clone your fork and start implementing your own application on top of baseAdmin.
5. (optional, but advised) Add the initial baseAdmin repository as an upstream remote:  
`git remote add upstream https://github.com/christophevg/baseAdmin`
6. Update your baseAdmin framework:  
`git fetch upstream; git checkout master; git merge upstream/master`  
(Hint: The top-level `Makefile` contains a target to do this: `make update`)

> The `backend` folder contains the baseAdmin server implementation, that also serves the actual baseAdmin pages. The original baseAdmin repository contains a backend folder that contains a demo application, which you can use to bootstrap your own application. Parts of the backend folder will never again be touched by commits to the original baseAdmin repository. These include the `app` folder. This folder contains the actual application, built on top of baseAdmin. this initially contains the demo application, which will not be changed anymore.

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
