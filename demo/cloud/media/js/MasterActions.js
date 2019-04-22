var MasterActions = Vue.component( "MasterActions", {
  template : `
<div>
  <h1>Perform actions on Master</h1>
  <center>
    <v-btn :loading="submittingReboot"   @click="submitReboot()"   class="primary">Reboot</v-btn>
    <v-btn :loading="submittingShutdown" @click="submitShutdown()" class="primary">Shutdown</v-btn>
    <v-btn :loading="submittingUpdate"   @click="submitUpdate()"   class="primary">Update</v-btn> (current: {{ version }})
  </center>
</div>`,
  computed: {
    version: function() {
      return store.state.version;
    }
  },
  methods: {
    submitReboot: function() {
      this.submittingReboot = true;
      var self = this;
      $.ajax({
        url: "/api/master/reboot",
        type: "POST",
        success: function(response) {
          app.$notify({
            group: "notifications",
            title: "Master Rebooting...",
            text:  "The Master is rebooting. Please wait a bit and refresh.",
            type:  "success",
            duration: 10000
          });
          self.submittingReboot = false;
        },
        error: function(response) {
          console.log(response);
          app.$notify({
            group: "notifications",
            title: "Failed to request reboot...",
            text:  response.statusText,
            type:  "warn",
            duration: 10000
          });
          self.submittingReboot = false;
        }
      });
    },
    submitShutdown: function() {
      this.submittingShutdown = true;
      var self = this;
      $.ajax({
        url: "/api/master/shutdown",
        type: "POST",
        success: function(response) {
          app.$notify({
            group: "notifications",
            title: "Master Shutting Down...",
            text:  "The Master is shutting down.",
            type:  "success",
            duration: 10000
          });
          self.submittingShutdown = false;
        },
        error: function(response) {
          app.$notify({
            group: "notifications",
            title: "Failed to request shutdown...",
            text:  response.statusText,
            type:  "warn",
            duration: 10000
          });
          self.submittingShutdown = false;
        }
      });
    },
    submitUpdate: function() {
      this.submittingUpdate = true;
      var self = this;
      $.ajax({
        url: "/api/master/update",
        type: "POST",
        success: function(response) {
          app.$notify({
            group: "notifications",
            title: "Master Updating...",
            text:  "The Master is updating. Please wait a bit and refresh.",
            type:  "success",
            duration: 10000
          });
          self.submittingUpdate = false;
        },
        error: function(response) {
          app.$notify({
            group: "notifications",
            title: "Failed to request update...",
            text:  response.statusText,
            type:  "warn",
            duration: 10000
          });
          self.submittingUpdate = false;
        }
      });
    }
  },
  data: function() {
    return {
      submittingReboot   : false,
      submittingShutdown : false,
      submittingUpdate   : false,
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
  path : "/master/actions"
});

router.addRoutes([{
  path      : "/master/actions",
  component : MasterActions
}]);
