var User = {
  template: `
  <div v-if="$route.params.id">
    <vue-form-generator ref="vfg" :schema="schema" :model="model" :options="formOptions" @validated="handleValidation"></vue-form-generator>
    <center><v-btn :loading="saving" @click="updateUser()" class="primary" :disabled="isUnchanged">Update</v-btn></center>
  </div>
  <div v-else>
    <v-btn fab class="white--text" color="green" @click="addUser()" style="float:right;">
      <v-icon>add</v-icon>
    </v-btn>
    <h1>Users</h1>
    <div style="margin-left: 25px;margin-bottom:10px;margin-right: 25px;">
      <v-layout wrap justify-space-around align-center>
        <v-btn v-for="user in users()" :key="user._id"
               @click="selectUser(user._id)"
               color="blue" class="white--text" round>
          <v-icon left>person</v-icon>
          {{ user.name }}
        </v-btn>
      </v-layout>
    </div>
  </div>`,
  created: function() {
    var self = this;
    $.get( "/api/users", function(users) {
      app.updateUsers(users);
      if(self.$route.params.id) {
        var user = store.getters.user(self.$route.params.id);
        if(user) {
          self.model["_id"]      = user["_id"];
          self.model["name"]     = user["name"];
          self.model["password"] = "";
        }
        self.$refs.vfg.validate();
      }      
    });
  },
  computed: {
    isUnchanged: function() {
      if( ! this.isValid ) { return true; }
      if(this.$route.params.id) {
        if(this.$route.params.id == "new") { return false; }
        var user = store.getters.user(this.$route.params.id);
        if(user) {
          if( this.model["name"] != user["name"] ) { return false; }
          if( this.model["password"] != "") { return false;}
        }
      }
      return true;
    }
  },
  methods: {
    users : function() {
      return store.getters.users();
    },
    selectUser: function(id) {
      this.$router.push("/user/" + id);
    },
    updateUser: function() {
      this.saving = true;
      var user = this.model;
      var self = this;
      $.ajax( { 
        url: "/api/user/" + user["_id"],
        type: "post",
        data: JSON.stringify(user),
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
          if(user["_id"] == "") {
            user["_id"] = response;
          }
          store.commit("upsertUser", user);
          self.saving = false;
        },
        failure: function(response) {
          console.log("whoops", response);
          self.saving = false;
        }
      });
    },
    handleValidation:function(isValid,errors){
      this.isValid = isValid;
    },
    addUser: function() {
      this.model["_id"] = "";
      this.model["name"] = "";
      this.model["password"] = "";
      this.$router.push("/user/new");
    }
  },
  watch: {
    "$route" : function(to, from) {
      if(this.$route.params.id) {
        var user = store.getters.user(this.$route.params.id);
        if(user) {
          this.model["_id"] = user["_id"];
          this.model["name"] = user["name"];
          this.model["password"] = "";
        }
      }
    }
  },
  data: function() {
    return {
      saving : false,
      isValid : true,
      model: {
        "_id" : "",
        "name": "",
        "password" : ""
      },
      schema: {
        fields: [
          {
            type: "input",
            inputType: "text",
            label: "ID",
            model: "_id",
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
            inputType: "text",
            label: "Password",
            model: "password",
            min: 6,
            required: false,
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
