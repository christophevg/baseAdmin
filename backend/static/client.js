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
      <component v-bind:is="currentTabComponent" class="tab"></component>
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
      if(! this.currentTab) { this.currentTab = store.state.services[0]; }
      return 'Client' + this.currentTab;
    }
  }
};

Vue.component( 'ClientClient', {
  template: `<div>Client...</div>`
});
