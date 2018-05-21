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

Vue.component( 'ClientStats', {
  template : `
  <v-layout column>
    <v-flex xs12>
      <v-container fluid grid-list-md class="grey lighten-4">
        <v-layout row wrap>
          <v-flex v-bind="{ ['xs{{chart.flex}}']: true }" v-for="(chart, id) in charts" :key="chart.title">
            <v-card>
              <v-card-title>
                <div>
                  <h3 class="headline mb-0">{{ chart.title }}</h3>
                </div>
              </v-card-title>
              <v-card-text>
                <div style="width: 100%;">
                  <line-chart :property="id" :chart-data="propertyChartData(id)" :height="chart.height"></line-chart>
                </div>
              </v-card-text>
              <v-card-actions class="white">
                <v-spacer></v-spacer>
                <v-btn icon @click="updateProperty(id)">
                  <v-icon>refresh</v-icon>
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-flex>
        </v-layout>
      </v-container>
    </v-flex>
  </v-layout>`,
  data: function() {
    return {
      charts: {
        prop1 : create_chart("prop1"),
        prop2 : create_chart("prop2")
      }
    }
  },
  methods: {
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
    }
  }
});

app.registerService("Stats");
