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
    clients: []
  },
  mutations: {
    updateProperty: function(state, update) {
      state.properties[update.id].labels = update.labels;
      state.properties[update.id].data   = update.data;
    },
    upsertClient: function(state, client) {
      // find current (if any)
      var current = state.clients.find(function(element) {
        return element._id == client._id;
      });
      // update or create current
      if(current) {
        for(var k in client) {
          current[k] = client[k];
        }
      } else {
        current = client;
      }
      // replace current (if any)
      state.clients = state.clients.filter(function(item) {
        return item._id != client._id;
      });
      // and add (new) current
      state.clients.push(current);
    }
  },
  getters: {
    groups: function(state) {
      return function() {
        var groups = {};
        for(var c in state.clients) {
          var client = state.clients[c];
          var client_groups = client.groups;
          for(var g in client_groups) {
            var group = client_groups[g];
            if(!(group in groups)) {
              groups[group] = {
                name: group,
                excerpt: " ",
                color: "green",
                icon: "check_circle",
                total: 0,
                clients: []
              }
            }
            groups[group].clients.push({
              title: client._id,
              color: client.status == "online" ? "green" : "red"
            });
            groups[group].total++;
            if(client.status != "online") {
              groups[group].color = "red";
              groups[group].icon  = "remove_circle";
            }
          }
        }
        return groups;
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
    drawer: null,
    sections: [
      { icon: 'home',      text: 'Home',      path: "/"          },
      { icon: 'dashboard', text: 'Dashboard', path: "/dashboard" },
      { icon: 'build',     text: 'Setup',     path: "/setup"     },
    ],
    charts: {
      prop1 : create_chart("prop1"),
      prop2 : create_chart("prop2")
    },
    headers: [
      { text: 'Client', align: 'left', sortable: true, value: 'name' }
    ],
    model: {
                id: 1,
                name: "John Doe",
                password: "J0hnD03!x4",
    						age: 35,
                skills: ["Javascript", "VueJS"],
                email: "john.doe@gmail.com",
                status: true
            },
            schema: {
                fields: [{
                    type: "input",
    								inputType: "text",
                    label: "ID",
                    model: "id",
                    readonly: true,
                    featured: false,
                    disabled: true
                }, {
                    type: "input",
    								inputType: "text",
                    label: "Name",
                    model: "name",
                    readonly: false,
                    featured: true,
                    required: true,
                    disabled: false,
                    placeholder: "User's name",
                    validator: VueFormGenerator.validators.string
                }, {
                    type: "input",
    								inputType: "password",
                    label: "Password",
                    model: "password",
                    min: 6,
                    required: true,
                    hint: "Minimum 6 characters",
                    validator: VueFormGenerator.validators.string
                }, {
                    type: "input",
                    inputType: "number",
                    label: "Age",
                    model: "age",
    								min: 18,
                    validator: VueFormGenerator.validators.number
                }, {
                    type: "input",
    								inputType: "email",
                    label: "E-mail",
                    model: "email",
                    placeholder: "User's e-mail address",
                    validator: VueFormGenerator.validators.email
                }, {
                    type: "checklist",
                    label: "Skills",
                    model: "skills",
                    multi: true,
                    required: true,
                    multiSelect: true,
                    values: ["HTML5", "Javascript", "CSS3", "CoffeeScript", "AngularJS", "ReactJS", "VueJS"]
                }, {
                   type: "switch",
                    label: "Status",
                    model: "status",
                    multi: true,
                    readonly: false,
                    featured: false,
                    disabled: false,
                    default: true,
    								textOn: "Active",
    								textOff: "Inactive"
                }]
            },

            formOptions: {
                validateAfterLoad: true,
                validateAfterChanged: true
            }
  },
  methods: {
    fixVuetifyCSS : function() {
      this.$vuetify.theme.info  = '#ffffff';
      this.$vuetify.theme.error = '#ffffff';
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
    removeClient: function(client) {
      this.$notify({
        group: "notifications",
        title: "<b>" + client + "</b> Offline",
        text:  "Client <b>" + client + "</b> just went offline.",
        type:  "error",
        duration: 10000
      });
      store.commit("removeClient", client);
    },
    selectedClient: function(client) {
      window.location = "/client";
    },
    editGroup : function(group) {
      console.log("edit group " + group);
    },
    upsertClient: function(client) {
      store.commit("upsertClient", client);
    },
    groups : function() {
      return store.getters.groups();
    }
  }
});

app.fixVuetifyCSS();
