# baseAdmin

A framework for managing distributed (IoT) applications, providing configuration distribution along with a web-based UI and REST backend interface.

## Work in Progress Warning ;-)

I've only just started working on this and I'm literally exploring my own code as I write it ;-) So until this warning is removed, I wouldn't trust myself using this ;-) Do play with it, but remember things can and will change overnight.

## Rationale

Having developed several (IoT) solutions that included an administrative backend, common patterns emerged. With baseAdmin I'm extracting the common parts into a framework that can be forked and extended for specific applications. The main goal is a have a working solution out of the box that can be extended with minimal (redundant) effort.

## Philosophy

The main goal of baseAdmin is out of the box functionality that is extendable with minimal effort. Therefore it is highly driven by conventions. Trying to break away from these conventions will result in pain. If you feel that any of the conventions don't fit your needs, you better don't use baseAdmin.

## What's in the Box?

![baseAdmin Overview](media/overview.png)

The minimal infrastructure you need is an `MQTT server`. Now you are ready to launch a `client` and have it join the MQTT network. Given some MQTT client, you can now publish configuration updates to the `client`.

Although a generic MQTT client is all you really need, having a `console` application supporting the protocol, might come in handy.

Because clients are sometimes offline, a `backend` offers additional services, such as configuration/logging consolidation & caching and a web/REST interface to consult this data from the `clients`.

## Technology Stack

This project stands on the shoulders of these wonderful high-power projects:

* Backend
  * [Python](https://www.python.org)
  * [Flask](http://flask.pocoo.org)
  * [Flask_Restful](http://flask-restful.readthedocs.io/en/latest/)
  * [Mongo DB](https://www.mongodb.com)
  * [MQTT](http://mqtt.org) e.g. [Eclipse Mosquitto](https://mosquitto.org)
* Frontend
  * [Vue.js](https://vuejs.org)
  * [Vuex](https://vuex.vuejs.org)
  * [Vuetify](https://vuetifyjs.com)
  * [Vue ChartJS](http://vue-chartjs.org)
  * [Paho Javascript Client](https://eclipse.org/paho/clients/js/)

## How to Use baseAdmin

Note: You can deploy this very easily on some Unix-based host. For some time now, I'm pretty happy with Heroku and given its generous free accounts, I'd advise you to try running your copy of baseAdmin there:

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

## Running baseAdmin Locally

Install dependencies: MongoDB and Mosquitto. Make sure Mosquitto is compiled with websockets support and enable a listener for it in the configuration file:

```
listener 1883

listener 9001 127.0.0.1
protocol websockets
```

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
(Hint: The top-level `Makefile` contains a target to do this: `make run`)

### Provisioning of data

When run for the first time, the Mongo database will be populated with collections with data. When a collection already exists, it will not be touched.

### Environment

To set environment variables, a `env.local` file can be created alongside `run.py`. (Hint: it's already in the `.gitignore` file)

The defaults for local development are:

```
APP_NAME=baseAdmin
MONGODB_URI=mongodb://localhost:27017/baseAdmin
CLOUDMQTT_URL=ws://localhost:9001/
```

When the environment contains a variable `PROVISION`, the mongo database will be reinitialised; collections are dropped and recreated. This is a useful thing while developing baseAdmin or your own application.

(Hint: The top-level `Makefile` contains a target to do this: `make devel`)

### Testing

Visit `http://localhost:5000/dashboard`. From a command prompt issue:

```bash
$  mosquitto_pub -h localhost -t "prop1" -m "updateProperty"
```

and watch the left/blue graph.
