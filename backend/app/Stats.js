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
  <v-layout v-if="stats()" column>
    <v-flex xs12>
      <v-container fluid grid-list-md class="grey lighten-4">
        <v-layout row wrap>
          <v-flex v-bind="{ ['xs{{chart.flex}}']: true }" v-for="(chart, id) in stats()" :key="chart.title">
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
    </v-flex>
  </v-layout>
  <div v-else>loading statistics...</div>`,
  created: function() {
    var id = this.$route.params.id;
    if( ! store.getters.client(id) ) {
      // create empty new client entry
      store.commit("newClient", {
        id: id,
        stats: [
          {
            stat : "idle", title: "Idle (%)",
            color: "#0567BA", height: 200, flex: 6,
            data: [], labels: []
          },
          {
            stat: "temperature", title: "Temperature",
            color: "#0567BA", height: 200, flex: 6,
            data: [], labels: []
          },
          {
            stat: "load", title: "Load 1m", index: 0,
            color: "#0567BA", height: 200, flex: 6,
            data: [], labels: []
          },
          {
            stat: "load", title: "Load 5m", index: 1,
            color: "#0567BA", height: 200, flex: 6,
            data: [], labels: []
          },
          {
            stat: "virtual_memory", title: "Memory Usage (%)", index: 2,
            color: "#0567BA", height: 200, flex: 6,
            data: [], labels: []
          },
          {
            stat: "disk_usage", title: "Disk Usage (%)", index: 3,
            color: "#0567BA", height: 200, flex: 6,
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
    }
  },
  methods: {
    stats: function() {
      var client = store.getters.client(this.$route.params.id);
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

app.registerService("Stats");

store.registerModule("stats", {
  state: {
    clients: []
  },
  mutations: {
    newClient: function(state, client) {
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
    client: function(state) {
      return function(id) {
        return state.clients.find(function(client) {
          return client.id == id;
        });
      }
    }
  }
});

(function() {

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

})();
