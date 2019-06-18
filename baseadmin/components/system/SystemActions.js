var MasterActions = Vue.component( "MasterActions", {
  template : `
<div>
  <h1>Perform actions on Master</h1>
  <center>
    <v-btn :loading="submitting['reboot']"   @click="submit('reboot')"   class="primary">Reboot</v-btn>
    <v-btn :loading="submitting['shutdown']" @click="submit('shutdown')" class="primary">Shutdown</v-btn>
    <v-btn :loading="submitting['update']"   @click="submit('update')"   class="primary">Update</v-btn> (current: {{ version }})
  </center>
</div>`,
  computed: {
    version: function() {
      return store.state.version;
    }
  },
  methods: {
    submit: function(cmd) {
      this.submitting[cmd] = true;
      var state = this;
      perform(cmd, {}, function(result) {
        if("success" in result && result.success) {
          app.$notify({
            group: "notifications",
            title: "Master will " + cmd + "...",
            text:  "The Master is going to " + cmd + ". Please wait a bit and refresh.",
            type:  "success",
            duration: 10000
          });
        } else  {
          app.$notify({
            group: "notifications",
            title: "Failed to " + cmd + "...",
            text:  "message" in result ? result.message : "unknown reason",
            type:  "warn",
            duration: 10000
          });
        }
        state.submitting[cmd] = false;
      });
    }
  },
  data: function() {
    return {
      submitting : {
        "reboot"  : false,
        "shutdown": false,
        "update"  : false
      },
    }
  }
});

var masterSection = app.sections.find(function(item) {
  return "group" in item && item.group && item.text == "Master";
});

if(! masterSection ) {
  masterSection = {
    group      : true,
    icon       : "home",
    text       : "Master",
    subsections: []
  }
  app.sections.push(masterSection);
}

masterSection.subsections.push({
  icon : "settings",
  text : "Actions",
  path : "/actions"
});

router.addRoutes([{
  path      : "/actions",
  component : MasterActions
}]);
