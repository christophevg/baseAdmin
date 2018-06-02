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
  <v-layout column>
    <v-flex xs12>
      <v-container fluid grid-list-md class="grey lighten-4">
        <v-layout row wrap>
          <v-flex v-bind="{ ['xs{{chart.flex}}']: true }" v-for="(chart, id) in stats" :key="chart.title">
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
                <v-btn icon @click="updateProperty(chart)">
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
      stats : {
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
      }
    }
  },
  methods: {
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
    },
    updateProperty: function(chart) {
      chart.data.push(chart.data.shift());
      chart.labels.push(chart.labels.shift());
    }
  }
});

app.registerService("Stats");
