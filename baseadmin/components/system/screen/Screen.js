Vue.component( 'ScreenComponent', {
  template: `
  <div v-if="refresh">
    <p>
      Normally the best HDMI settings are detected automatically. If this is
      not the case, a combination of an HDMI Group and Mode can fix this. For a
      full list of possible combinations see the <a target="_blank" 
      href="https://www.raspberrypi.org/documentation/configuration/config-txt/video.md">video options page</a> on the Raspberry Pi website.
    </p>
    <br>
    <vue-form-generator :useless="refresh" :schema="schema" :model="model" :options="formOptions"></vue-form-generator>
    <center>
      <v-btn :loading="saving" @click="update()" class="primary" :disabled="model.isUnchanged">Update</v-btn>
    </center>
  </div>
  `,
  methods: {
    update: function() {
      this.saving = true;
      execute_on(this.$route.params.id, "screen", {
        "hdmi"       : this.model.hdmi,
        "orientation": this.model.orientation
      })
      this.saving = false;
      this.model.isUnchanged = true;
    }
  },
  computed: {
    refresh: function() {
      if(this.$route.params.scope == "group") { return true; }
      var client = store.getters.client(this.$route.params.id);
      try {
        this.model.hdmi        = client.state.current.hdmi;
        this.model.orientation = client.state.current.orientation;
      } catch(err) {}
      return client;
    }
  },
  data: function() {
    return {
      initialized: false,
      saving : false,
      model: {
        isUnchanged: true,
        hdmi : {
          group: "",
          mode : ""
        },
        orientation : null
      },
      schema: {
        fields: [
          {
            type: "input",
            inputType: "text",
            label: "HDMI Group",
            model: "hdmi.group",
            hint: "(e.g. for 1080p 50Hz use group=1 (CEA))",
            onChanged: function(model, newVal, oldVal, field) {
              model.isUnchanged = false;
            }
          },
          {
            type: "input",
            inputType: "text",
            label: "HDMI Mode",
            model: "hdmi.mode",
            hint: "(e.g. for 1080p 50Hz use mode=31)",
            onChanged: function(model, newVal, oldVal, field) {
              model.isUnchanged = false;
            }
          },
          {
            type: "select",
            inputType: "text",
            label: "Orientation",
            model: "orientation",
            values: [
              {  id :   "D", name: "Default - no rotation applied." },
              {  id :  "CW", name: "Clockwise - rotated 90 degrees to the right." },
              {  id :  "UD", name: "Upside Down - rotated 180 degrees." },
              {  id : "CCW", name: "Counter Clockwise - rotated 90 degrees to the left." }
            ],
            onChanged: function(model, newVal, oldVal, field) {
              model.isUnchanged = false;
            }
          },
        ]
      },
      formOptions: {
        validateAfterLoad: true,
        validateAfterChanged: true
      }
    }
  }
});

app.registerClientComponent("Screen");
app.registerGroupComponent("Screen");
