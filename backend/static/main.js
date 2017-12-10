Vue.component('line-chart', {
  extends:  VueChartJs.Line,
  mixins: [ VueChartJs.mixins.reactiveProp],
  props:  [ 'chartData' ],
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
    cards: [
      {
        datacollection : {
          labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
          datasets: [
            {
              label: 'Set 1',
              backgroundColor: "#0567BA",
              data: [ 40, 39, 10, 40, 39, 80, 40 ]
            }
          ]
        },
        title: "Property 1",
        flex: 6
      },
      {
        datacollection : {
          labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
          datasets: [
            {
              label: 'Set 2',
              backgroundColor: "#0567BA",
              data: [ 40, 39, 10, 40, 39, 80, 40 ]
            }
          ]
        },
        title: "Property 2",
        flex: 6
      }
    ]
  },
  props: {
    source: String
  },
  methods: {
    updateChart: function(card) {
      var labels = card.datacollection.labels,
          data   = card.datacollection.datasets[0].data;
      labels.push(labels.shift());
      data.push(data.shift());
      // don't update datacollection directly, create a new object !
      card.datacollection = {
        labels: labels,
        datasets: [
          {
            label: card.datacollection.datasets[0].label,
            backgroundColor: card.datacollection.datasets[0].backgroundColor,
            data: data
          }
        ]
      }
    }
  }
});
