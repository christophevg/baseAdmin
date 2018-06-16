var Log = {
  template : `
<v-layout justify-center column>
  <v-card v-for="(message, i) in messages()" :key="i">
    <v-card-title>
      <div>
        <span class="grey--text">{{ message.topic }}</span><br>
        <span>{{ message.payload }}</span>
      </div>
    </v-card-title>
  </v-card>
</v-layout>`,
  methods: {
    messages : function() {
      return store.getters.messages();
    }
  }
};
