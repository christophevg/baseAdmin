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

Vue.component( 'ClientStats', {
  template : `
<div>
<v-container fluid v-if="stats()" grid-list-xl text-xs-center>
  <v-layout row wrap>
    <v-flex xs12 md6 v-for="(chart, id) in stats()" :key="chart.title">
      <v-card>
        <v-card-title>
          <div>
            <h3 class="headline mb-0">{{ chart.title }}</h3>
          </div>
        </v-card-title>
        <v-card-text>
          <div style="width: 100%;">
            <line-chart :property="id" :chart-data="propertyChartData(chart)" :height="chart.height"></line-chart>
          </div>
        </v-card-text>
        <v-card-actions class="white">
          <v-spacer></v-spacer>
          <v-btn v-if="false" icon @click="">
            <v-icon>refresh</v-icon>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-flex>
  </v-layout>  
</v-container>
<div v-else>loading statistics...</div>
<div>
    <vue-form-generator :schema="schema" :model="model" :options="formOptions"></vue-form-generator>
    <center>
      <v-btn :loading="saving" @click="updateInterval()" class="primary" :disabled="model.isUnchanged">Update</v-btn>
    </center>
</div>
</div>`,
  created: function() {
    var id = this.$route.params.id;
    if( ! store.getters.clientStats(id) ) {
      // create empty new client entry
      store.commit("newClientStats", {
        id: id,
        stats: [
          {
            stat : "idle", title: "Idle (%)",
            color: "#0567BA", height: 200,
            data: [], labels: []
          },
          {
            stat: "temperature", title: "Temperature",
            color: "#0567BA", height: 200,
            data: [], labels: []
          },
          {
            stat: "load", title: "Load 1m", index: 0,
            color: "#0567BA", height: 200,
            data: [], labels: []
          },
          {
            stat: "load", title: "Load 5m", index: 1,
            color: "#0567BA", height: 200,
            data: [], labels: []
          },
          {
            stat: "virtual_memory", title: "Memory Usage (%)", index: 2,
            color: "#0567BA", height: 200,
            data: [], labels: []
          },
          {
            stat: "disk_usage", title: "Disk Usage (%)", index: 3,
            color: "#0567BA", height: 200,
            data: [], labels: []
          }
        ]
      });
      // retrieve history data
      $.get( "/api/client/" + id + "/stats", function( stats ) {
        for(var s=stats.length-1; s>-1; s--) {
          store.dispatch( "updateStats", {
            client : id,
            stats  : stats[s]
          });
        }
      });
      // load stats config/interval
      var client = store.getters.client(id);
      if( client ) {
        try {
          this.model.interval = client.services.ReportingService.config.interval;
        } catch {
          console.log("could not load interval");
        }
      } else {
        var self = this;
        $.get( "/api/client/" + id, function(client) {
          app.upsertClient(client);
          client = store.getters.client(id);
          this.model.interval = client.services.ReportingService.config.interval;          
        });
      }
    }
  },
  data: function() {
    return {
      saving : false,
      model: {
        interval: null,
        isUnchanged: true
      },
      schema: {
        fields: [{
          type: "input",
          inputType: "number",
          label: "Interval",
          model: "interval",
          min: 60,
          validator: VueFormGenerator.validators.number,
          onChanged: function(model, newVal, oldVal, field) {
            model.isUnchanged = false;
          }
        }]
      },
      formOptions: {
        validateAfterLoad: true,
        validateAfterChanged: true
      }
    }
  },
  methods: {
    updateInterval: function() {
      this.saving = true;
      var id = this.$route.params.id;
      var self = this;
      MQ.publish("client/" + id + "/service/ReportingService", {
        "uuid" : uuid(),
        "config" : { "interval" : this.model.interval }
      });
      // TODO: handle this from own/incoming message?
      store.commit("serviceUpdate", {
        client: id,
        service: "ReportingService",
        config: { "interval" : this.model.interval }
      });
      var client = store.getters.client(id);
      this.model.interval = client.services.ReportingService.config.interval;
      this.saving = false;
      this.model.isUnchanged = true;
    },
    stats: function() {
      var client = store.getters.clientStats(this.$route.params.id);
      if( client ) {
        return client.stats;
      }
      return null;
    },
    propertyChartData: function(chart) {
      return {
        labels: chart.labels,
        datasets : [
          {
            label: chart.title,
            backgroundColor: chart.color,
            data: chart.data
          }
        ]
      }
    }
  }
});

app.registerService({
  name            : "ReportingService",
  location        : "http://localhost:18181",
});

app.registerClientComponent("Stats");

store.registerModule("stats", {
  state: {
    clients: []
  },
  mutations: {
    newClientStats: function(state, client) {
      state.clients.push(client);
    },
    updatedClientStat: function(state, update) {
      var client = state.clients.find(function(client) {
        return client.id == update.client;
      });
      if(! client ) { return; }
      var stats = client.stats.filter(function(stat) {
        return stat.stat == update.stat;
      });
      for(var stat in stats) {
        if(stats[stat].data.length > 12) {
          stats[stat].data.shift();
          stats[stat].labels.shift();
        }
        // apply optional indexing
        var value = "index" in stats[stat]
          ? update.value[stats[stat].index]
          : update.value;
        stats[stat].data.push(value);
        // format timestamp for graph
        var day   = update.when.getDate()  + "/" + (update.when.getMonth()+1);
        var now   = new Date();
        var today = now.getDate()  + "/" + (now.getMonth()+1);
        var ts    = ( day == today ? ""  : day + " ") +
                    ("0" + update.when.getHours()).substr(-2) + ":" +
                    ("0" + update.when.getMinutes()).substr(-2) + ":" +
                    ("0" + update.when.getSeconds()).substr(-2);
        stats[stat].labels.push(ts);
      }
    }
  },
  actions: {
    updateStats: function(context, update) {
      var client = context.getters.client(update.client);
      if( ! client ) { return; }
      for(var stat in update.stats) {
        context.commit("updatedClientStat", {
          client : update.client,
          stat   : stat,
          value  : update.stats[stat],
          when   : new Date(update.stats["system_time"]*1000)
        });
      }
    }
  },
  getters: {
    clientStats: function(state) {
      return function(id) {
        return state.clients.find(function(client) {
          return client.id == id;
        });
      }
    }
  }
});

$( document ).ready(function() {
  store.subscribe( function(mutation, state) {
    if( mutation.type == "newMessage"
     && mutation.payload.topic.length == 5
     && mutation.payload.topic[4] == "stats")
    {
      store.dispatch( "updateStats", {
        client : mutation.payload.topic[1],
        stats  : mutation.payload.payload
      });
    }
  });
});
