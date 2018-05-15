var store = new Vuex.Store({
  state: {
    properties : {
      prop1: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        data: [ 40, 39, 10, 40, 39, 80, 40 ],
        color: "#0567BA",
        title: 'Property 1',
        flex: 6,
        height: 200
      },
      prop2: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        data: [ 40, 39, 10, 40, 39, 80, 40 ],
        color: "#ff0000",
        title: 'Property 2',
        flex: 6,
        height: 200
      }
    },
    mqtt : {
      clients: []
    }
  },
  mutations: {
    updateProperty: function(state, update) {
      state.properties[update.id].labels = update.labels;
      state.properties[update.id].data   = update.data;
    },
    removeClient: function(state, client) {
      state.mqtt.clients = state.mqtt.clients.filter(function (el) {
        return el.name != client;
      });
    },
    addClient: function(state, client) {
      var clients = state.mqtt.clients.filter(function (el) {
        return el.name != client;
      });
      clients.push({"name" : client});
      state.mqtt.clients = clients;
    }
  },
  getters: {
    clients: function(state) {
      return function() {
        return state.mqtt.clients;
      }
    },
    propertyData: function(state) {
      return function(id) {
        return state.properties[id].data;
      }
    },
    propertyLabels: function(state) {
      return function(id) {
        return state.properties[id].labels;
      }
    }
  }
});

Vue.component('line-chart', {
  extends:  VueChartJs.Line,
  mixins: [ VueChartJs.mixins.reactiveProp ],
  props:  [ "options" ],
  mounted: function() {
    this.renderChart(
      this.chartData,
      {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          display: false
        }
      }
    );
  }
});

function create_chart(prop) {
  var data = store.state.properties[prop]; 
  return {
    title:  data.title,
    height: data.height,
    color:  data.color,
    flex:   data.flex
  };
}

var app = new Vue({
  el: "#app",
  delimiters: ['${', '}'],
  data: {
    message: "Dashboard message from Vue",
    drawer: null,
    items: [
      { icon: 'home',    text: 'Home',      path: "/"          },
      { icon: 'history', text: 'Dashboard', path: "/dashboard" },
    ],
    charts: {
      prop1 : create_chart("prop1"),
      prop2 : create_chart("prop2")
    },
    headers: [
      { text: 'Client', align: 'left', sortable: true, value: 'name' }
    ]
  },
  methods: {
    clients: function() {
      return store.getters.clients();
    },
    propertyChartData: function(id) {
      return {
        labels: this.propertyLabels(id),
        datasets : [
          {
            label: this.charts[id].title,
            backgroundColor: this.charts[id].color,
            data: this.propertyData(id)
          }
        ]
      }
    },
    propertyData: function(id) {
      return store.getters.propertyData(id);
    },
    propertyLabels: function(id) {
      return store.getters.propertyLabels(id);
    },
    updateProperty: function(id) {
      var data   = this.propertyData(id);
          labels = this.propertyLabels(id);
      data.push(data.shift());
      labels.push(labels.shift());
      store.commit("updateProperty", {
        id: id,
        data: data,
        labels: labels
      })
    },
    addClient: function(client) {
      store.commit("addClient", client);
    },
    removeClient: function(client) {
      this.$notify({
        group: "notifications",
        title: "<b>" + client + "</b> Offline",
        text:  "Client <b>" + client + "</b> just went offline.",
        type:  "error",
        duration: 10000
      });
      store.commit("removeClient", client);
    }
  }
});
