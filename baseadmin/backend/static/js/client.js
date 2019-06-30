function byName(a, b) {
  if( a < b ) {
    return -1;
  }
  if( a > b ){
    return 1;
  }
  return 0;
}


var Client = {
  template: `
<div id="dynamic-component-demo" class="demo">
  <h1>
    <v-btn color="red" fab style="float:right;" small dark @click="release()">
      <v-icon>delete</v-icon>
    </v-btn>
    {{ $route.params.id }}
    <v-icon :color="clientColor" x-large>{{ clientIcon }}</v-icon>
  </h1>
  <hr><br>
  <button
    v-for="tab in tabs"
    v-bind:key="tab"
    v-bind:class="['tab-button', { active: currentTab === tab }]"
    v-on:click="currentTab = tab"
  >{{ tab }}</button>

  <div v-if="tabs.length" class="panel panel-default">
    <div class="panel-body">
      <component v-if="currentTabComponent" v-bind:is="currentTabComponent" class="tab"></component>
    </div>
  </div>
  <div v-else>
    <p v-if="group">
      Groups have no configuration options. Add options using 'app.registerGroupComponents'.
    </p>
    <p v-else>
      Clients have no configuration options. Add options using 'app.registerClientComponents'.
    </p>
  </div>

  <div v-if="client && client.queue && client.queue.length > 0">
    <h2>Queued</h2>
    <ul>
      <li v-for="item in client.queue">{{ item }}</li>
    </ul>
  </div>

  <div v-if="client && client.state && client.state.futures && client.state.futures.length > 0">
    <h2>Scheduled</h2>
    <ul>
      <li v-for="item in client.state.futures">{{ item }}</li>
    </ul>
  </div>

</div>`,
  data: function() {
    return {
      currentTab: null,
    }
  },
  computed: {
    client: function() {
      return store.getters.client(this.$route.params.id);
    },
    clientColor: function() {
      return this.client && this.client.connected ? "green" : "red";
    },
    clientIcon: function() {
      return this.client && this.client.connected ? "check_circle" : "remove_circle";      
    },
    group: function() {
      if( this.$route.params.scope != "group" ) { return null; }
      return store.getters.group(this.$route.params.id);
    },
    tabs: function() {
      return store.state.clientComponents["client"].sort(byName);
    },
    currentTabComponent: function () {
      if(! this.currentTab) {
        if(this.tabs.length > 0) {
          this.currentTab = this.tabs[0];
        } else {
          return null;
        }
      }
      return this.currentTab + "Component";
    },
  },
  methods: {
    release: function() {
      release(this.$route.params.id);
      this.$router.push("/dashboard");
    }
  }
};
