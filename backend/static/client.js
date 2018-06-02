var Client = {
  template: `
<div id="dynamic-component-demo" class="demo">
  <button
    v-for="tab in tabs"
    v-bind:key="tab"
    v-bind:class="['tab-button', { active: currentTab === tab }]"
    v-on:click="currentTab = tab"
  >{{ tab }}</button>

  <div class="panel panel-default">
    <div class="panel-body">
      <component v-if="currentTabComponent" v-bind:is="currentTabComponent" class="tab"></component>
    </div>
  </div>
</div>`,
  data: function() {
    return {
      currentTab: null,
      tabs: store.state.services
    }
  },
  computed: {
    currentTabComponent: function () {
      if(! this.currentTab) {
        if(store.state.services.length > 0) {
          this.currentTab = store.state.services[0];
        } else {
          return null;
        }
      }
      return 'Client' + this.currentTab;
    }
  }
};

// subscribe to store events and handle online/offline events

$( document ).ready(function() {
  store.subscribe( function(mutation, state) {
    if( mutation.type == "newMessage"
     && mutation.payload.topic.length == 2
     && mutation.payload.topic[0] == "client"
     && "status" in mutation.payload.payload )
    {
      app.upsertClient({
        "_id"    : mutation.payload.topic[1],
        "status" : mutation.payload.payload.status
      });
    }
  });
});
