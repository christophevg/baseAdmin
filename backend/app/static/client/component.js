var Client = {
  template: `
<div id="dynamic-component-demo" class="demo">
  <button
    v-for="tab in tabs"
    v-bind:key="tab"
    v-bind:class="['tab-button', { active: currentTab === tab }]"
    v-on:click="currentTab = tab"
  >{{ tab }}</button>

  <component v-bind:is="currentTabComponent" class="tab"></component>
</div>`,
  data: function() {
    return {
      currentTab: 'Stats',
      tabs: [ 'Stats', 'Form' ]
    }
  },
  computed: {
    currentTabComponent: function () {
      return 'Client' + this.currentTab
    }
  }
};

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

Vue.component( 'ClientForm', {
  template: `
<div class="panel panel-default">
  <div class="panel-body">
    <vue-form-generator :schema="schema" :model="model" :options="formOptions"></vue-form-generator>
  </div>
</div>
  `,
  data: function() {
    return {
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
    }
  },
  methods: {}
});
