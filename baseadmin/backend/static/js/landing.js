var Landing = {
  template : `
<div>
  <div v-if="provision">
    <h1>One-time setup</h1>
    <div>
      This is the first time you access this application. You must create a
      first user to be able to authenticate and access it.<br><br>
      <vue-form-generator ref="vfg" :schema="schema" :model="model" :options="formOptions" @validated="handleValidation"></vue-form-generator>
      <v-btn :loading="working" @click="createUser()" class="primary" :disabled="isInvalid">Create User</v-btn>
      </center>
    </div>
  </div>
  <div v-else> 
    <h1>Welcome...</h1>
    <div>
      If you are authorized to access this application, use the button below to
      log on and access your dashboard...<br>
      <v-btn href="/dashboard" color="primary" class="white--text">
        Log on...
      </v-btn>
    </div>
  </div>
</div>
`,
  computed: {
    provision: function() {
      return store.state.provision;
    },
    isInvalid: function() {
      if( ! this.isValid ) { return true; }
      return this.model["name"] == "" ||
             this.model["pass"] == "";
    }
  },
  methods: {
    handleValidation:function(isValid,errors){
      this.isValid = isValid;
    },
    createUser: function() {
      this.creating = true;
      var provision = { 
        "user" : {
          "name": this.model["name"],
          "pass": this.model["pass"]
        }
      };
      var self = this;
      $.ajax( {
        url: "/api/provision",
        type: "post",
        data: JSON.stringify(provision),
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
          self.working = false;
          window.location = "/dashboard";
        },
        error: function(response) {
          app.$notify({
            group: "notifications",
            title: "Could not save user...",
            text:  response.responseText,
            type:  "warn",
            duration: 10000
          });
          self.working = false;
        }
      });
    }
  },
  data: function() {
    return {
      working: false,
      isValid : true,
      model: {
        "name": "",
        "pass": ""
      },
      schema: {
        fields: [
          {
            type: "input",
            inputType: "text",
            label: "Name",
            model: "name",
            readonly: false,
            required: true,
            placeholder: "User's name",
            validator: VueFormGenerator.validators.string
          }, {
            type: "input",
            inputType: "text",
            label: "Password",
            model: "pass",
            min: 6,
            required: true,
            validator: VueFormGenerator.validators.string
          }
        ]
      },
      formOptions: {
        validateAfterLoad: false,
        validateAfterChanged: true
      }
    }
  }
};
