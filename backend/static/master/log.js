var Log = {
  template : `
<div>
  <h1>Logged Activity</h1>
  <v-layout justify-center column>
    <v-card v-for="(message, i) in messages" :key="i">
      <v-card-title>
        <div>
          <div style="display:inline-block;width:155px;text-align:center;margin-right:5px;">{{ message.when }}</div> 
  
          <v-btn v-if="message.client" depressed small color="primary" @click="gotoClient(message.client)">
            {{ message.client }}
          </v-btn>
          <div v-else class="grey--text">{{ message.topic }}</div>
          <span>{{ message.payload }}</span>
        </div>
      </v-card-title>
    </v-card>
  </v-layout>
</div>`,
  computed: {
    messages : function() {
      var messages = store.getters.messages();
      for(var i in messages) {
        messages[i]["client"] =
          messages[i].topic[0] == "client" ? messages[i].topic[1] : false;
      }
      return messages;
    }
  },
  methods: {
    gotoClient: function(client) {
      this.$router.push("/client/" + client);
    }
  }
};
