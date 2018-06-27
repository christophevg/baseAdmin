var Dashboard = {
  template : `
<v-layout justify-center column>
  <v-expansion-panel popout>
    <v-expansion-panel-content v-for="(group, i) in groups" :key="i" hide-actions>
      <v-layout slot="header" align-center row spacer>
        <v-flex xs4 sm2 md1>
          <v-avatar slot="activator" size="36px">
            <v-icon :color="group.color" large>{{ group.icon }}</v-icon>
          </v-avatar>
        </v-flex>
        <v-flex sm5 md3 hidden-xs-only>
          <strong v-html="group.name"></strong>
          <span v-if="group.total" class="grey--text">&nbsp;({{ group.total }})</span>
        </v-flex>
        <v-flex v-if="group.excerpt" class="grey--text" ellipsis hidden-sm-and-down>
          &mdash;
          {{ group.excerpt }}
        </v-flex>
      </v-layout>

      <div style="float:left;margin-left:15px;">
      <v-btn color="primary" fab small dark @click="editGroup(group.name)">
        <v-icon>edit</v-icon>
      </v-btn>
    </div>

      <div style="margin-left: 25px;margin-bottom:10px;margin-right: 25px;">
        <v-layout wrap justify-space-around align-center>
          <v-btn v-for="client in group.clients" :key="client.title" @click="selectedClient(client.title); return false;"
                 :color="client.color" class="white--text" round>
            {{ client.title }}
          </v-btn>
        </v-layout>
      </div>

    </v-expansion-panel-content>
  </v-expansion-panel>
  <center>
    <v-btn @click.stop="createGroupDialog=true" fab color="primary">
      <v-icon>add</v-icon>
    </v-btn>
  </center>
  <v-dialog v-model="createGroupDialog" max-width="500px">
    <v-card>
      <v-card-title>Create new Group</v-card-title>
      <v-card-text>
        <vue-form-generator :schema="schema" :model="model" :options="formOptions"></vue-form-generator>
      </v-card-text>
      <v-card-actions>
        <v-btn color="secondary" flat @click.stop="createGroupDialog=false">Close</v-btn>
        <v-btn color="primary"   flat @click.stop="createGroup()">Add</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</v-layout>`,
  data: function() {
    return {
      more_groups : [],
      createGroupDialog: false,
      model: {
        name: ""
      },
      schema: {
        fields: [{
          type: "input",
          inputType: "text",
          label: "name",
          model: "name",
        }]
      },
      formOptions: {
        validateAfterLoad: true,
        validateAfterChanged: true
      }
    }
  },
  computed: {
    groups : function() {
      var g = store.getters.groups();
      for(var i in this.more_groups) {
        g[this.more_groups[i]] = {
          name: this.more_groups[i],
          excerpt: " ",
          color: "green",
          icon: "check_circle",
          total: 0,
          clients: []
        }
      }
      return g;
    }
  },
  methods: {
    selectedClient: function(client) {
      this.$router.push('/client/' + client);
    },
    editGroup : function(group) {
      this.$router.push('/group/' + group);
    },
    createGroup: function() {
      if( this.model.name != "" ) {
        this.more_groups.push(this.model.name);
        this.model.name = "";
      }
      this.createGroupDialog = false;
    }
  }
};
