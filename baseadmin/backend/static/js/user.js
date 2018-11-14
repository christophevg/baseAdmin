var User = {
  template: `
  <div v-if="$route.params.id">
    <vue-form-generator ref="vfg" :schema="schema" :model="model" :options="formOptions" @validated="handleValidation"></vue-form-generator>
    <center>
      <v-btn :loading="creating" @click="createUser()" class="primary"   :disabled="isInvalid"   v-if="isNew">Create</v-btn>
      <v-btn :loading="saving"   @click="updateUser()" class="primary"   :disabled="isUnchanged" v-if="!isNew">Update</v-btn>
      <v-btn :loading="deleting" @click="removeUser()" class="important"                         v-if="isRemovable">Remove</v-btn>
    </center>
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
      app.allUsers(users);
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
    },
    isInvalid: function() {
      if( ! this.isValid ) { return true; }
      return this.model["_id"]      == "" || 
             this.model["name"]     == "" ||
             this.model["password"] == "";
    },
    isNew: function() {
      return this.$route.params.id == "new";
    },
    isRemovable: function() {
      return ! this.isNew && this.model["_id"] != "admin";
    }
  },
  methods: {
    users : function() {
      return store.getters.users();
    },
    selectUser: function(id) {
      this.$router.push("/user/" + id);
    },
    createUser: function() {
      this.creating = true;
      var user = { 
        "_id" : this.model["_id"],
        "name": this.model["name"],
        "password" : this.model["password"]
      };
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
          store.commit("newUser", user);
          self.creating = false;
          self.selectUser(user["_id"]);
        },
        error: function(response) {
          app.$notify({
            group: "notifications",
            title: "Could not save user...",
            text:  response.responseJSON.message,
            type:  "warn",
            duration: 10000
          });
          self.creating = false;
        }
      });
    },
    updateUser: function() {
      this.saving = true;
      var user = { 
        "_id" : this.model["_id"],
        "name": this.model["name"],
        "password" : this.model["password"]
      };
      var self = this;
      $.ajax( { 
        url: "/api/user/" + user["_id"],
        type: "put",
        data: JSON.stringify(user),
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
          store.commit("updatedUser", user);
          self.saving = false;
        },
        error: function(response) {
          app.$notify({
            group: "notifications",
            title: "Could not save user...",
            text:  response.responseJSON.message,
            type:  "warn",
            duration: 10000
          });
          self.saving = false;
        }
      });
    },
    removeUser: function() {
      this.deleting = true;
      var user = this.model;
      var self = this;
      $.ajax( {
        url: "/api/user/" + user["_id"],
        type: "delete",
        success: function(response) {
          store.commit("removedUser", user);
          self.deleting = false;
          app.$notify({
            group: "notifications",
            title: "Success",
            text: "User " + user["_id"] + " was successfully removed.",
            type: "success",
            duration: 10000
          });
          app.$router.push("/user");
        },
        error: function(response) {
          app.$notify({
            group: "notifications",
            title: "Could not remove user...",
            text:  response.responseJSON.message,
            type:  "warn",
            duration: 10000
          });
          self.deleting = false;
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
      app.$router.push("/user/new");
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
      creating: false,
      saving : false,
      deleting: false,
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
            label: "login",
            model: "_id",
            required: true,
            readonly: false,
            disabled: function(model) {
              return ! this.$parent.isNew;
            }
          }, {
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
            model: "password",
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
