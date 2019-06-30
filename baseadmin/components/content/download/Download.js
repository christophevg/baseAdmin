// cli support

function add_file(name, file, url) {
  var group = store.getters.group(name);
  if(group) {
    group.forEach(function(member) {
      add_file_to_client(member, file, url);
    });
  } else {
    add_file_to_client(name, file, url);
  }
}

function add_file_to_client(name, file, url) {
  execute_on(name, "addFile", { name: file, url: url });
}

function remove_file(name, file) {
  var group = store.getters.group(name);
  if(group) {
    group.forEach(function(member) {
      remove_file_from_client(member, file);
    });
  } else {
    remove_file_from_client(name, file);
  }  
}

function remove_file_from_client(name, file) {
  execute_on(name, "removeFile", { name: file });
}

// component

Vue.component( "ContentComponent", {
  template : `
<div v-if="groups_are_loaded">
  <div v-if="scope == 'client'">
    <h1>Content on client</h1>
    <v-data-table
      :headers="headers"
      :items="files"
      hide-actions
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.name }}</td>
        <td class="text-xs-right">{{ props.item.size }}</td>

        <td v-if="props.item.time > 0" class="text-xs-right">{{ props.item.time }}</td>
        <td v-else class="text-xs-right"><v-icon color="blue">cloud_download</v-icon></td>
        <td width="1%">
          <v-btn color="red" fab small dark @click="deleteFile(props.item.name)">
            <v-icon>delete</v-icon>
          </v-btn>
        </td>
      </template>
    </v-data-table>
  </div>
  <h1>Available content</h1>
  <v-data-table
    :headers="masterHeaders"
    :items="masterFiles"
    hide-actions
    class="elevation-1"
  >
    <template slot="items" slot-scope="props">
      <td>{{ props.item.name }}</td>
      <td class="text-xs-right">{{ props.item.size }}</td>
      <td width="1%">
        <v-btn color="green" fab small dark @click="addFile(props.item.name)">
          <v-icon>add_circle</v-icon>
        </v-btn>
      </td>
    </template>
  </v-data-table>
</div>`,
  computed: {
    scope: function() {
      return this.$route.params.scope;
    },
    groups_are_loaded: function() {
      return store.getters.groups_loaded();
    },
    isGroup: function() {
      return "scope" in this.$route.params && this.$route.params.scope == "group";
    },
    files: function() {
      if(this.$route.params.scope == "client") { //   group
        var client = store.getters.client(this.$route.params.id);
        if(client) {
          return client.state.current.files;
        }
      }
      return [];
    },
    masterFiles: function() {
      var computed = this;
      return store.getters.files.filter(function(masterItem){
        return ! computed.files.find(function(item){
          return masterItem.name == item.name;
        });
      });
    }
  },
  methods: {
    addFile: function(name) {
      this.saving = true;
      var url = "ftp://" + window.location.hostname + "/" + name;
      add_file(this.$route.params.id, name, url);
      this.saving = false;
      this.model.isUnchanged = true;
    },
    deleteFile: function(name) {
      remove_file(this.$route.params.id, name);
    }
  },
  data: function() {
    return {
      headers: [
        {
          text: 'Name',
          align: 'left',
          sortable: true,
          value: 'name'
        },
        {
          text: 'Size',
          align: 'right',
          value: 'size'
        },
        {
          text: 'Download time',
          align: 'right',
          value: 'time'
        }
      ],
      masterHeaders: [
        {
          text: 'Name',
          align: 'left',
          sortable: true,
          value: 'name'
        },
        {
          text: 'Size',
          align: 'right',
          value: 'size'
        }
      ],
      saving : false,
      model: {
        file: "",
        files: [],
        isUnchanged: true,
        when: null,
        config: {
          "content" : ""
        }
      },
      schema: {
        fields: [
          {
            type: "select",
            label: "File",
            model: "file",
            selectOptions: {
              value: "name"
            },
            values: function() {
              return store.getters.serverContent().list;
            },
            onChanged: function(model, newVal, oldVal, field) {
              model.isUnchanged = false;
            }
          }
        ]
      },
      formOptions: {
        validateAfterLoad: true,
        validateAfterChanged: true
      }
    }
  }
});

app.registerClientComponent("Content");
app.registerGroupComponent("Content");

// app.registerService({
//   name            : "Content",
//   location        : "http://localhost:38383",
// });

// store.registerModule("content", {
//   state: {
//     clients: []
//   },
//   mutations: {
//     content: function(state, content) {
//       state.clients.push(content);
//     },
//     file: function(state, update){
//       var id     = update["client"],
//           file   = update["file"],
//           client = store.getters.content(id);
//       client.files = client.files.filter(function(item) {
//         return item.name != file.name;
//       });
//       client.files.push(file);
//     }
//   },
//   actions: {
//     initClient: function(context, id) {
//       var client = context.state.clients.find(function(client) {
//         return client.id == id;
//       });
//       if(! client ) {
//         client = {
//           id    : id,
//           files : [],
//           loaded: false
//         }
//         store.commit("content", client );
//       }
//       if(! client.loaded) {
//         $.ajax({
//           url: "/api/content/" +id,
//           type: "GET",
//           success: function(files) {
//             for(var i in files) {
//               context.commit("file", {
//                 client: id,
//                 file  : files[i]
//               });
//             }
//             client.loaded = true;
//           },
//           error: function(response) {
//             // probably no content recorded yet
//             client.loaded = true;
//           }
//         });
//       }
//     }
//   },
//   getters: {
//     content: function(state) {
//       return function(id) {
//         var client = state.clients.find(function(client) {
//           return client.id == id;
//         });
//         if(! client ) {
//           client = {
//             id    : id,
//             files : [
//               {
//                 "time" : "default",
//                 "name" : "index.html",
//                 "size" : 3058
//               },
//               {
//                 "time" : "default",
//                 "name" : "black.html",
//                 "size" : 44
//               },
//               {
//                 "time" : "default",
//                 "name" : "splash.png",
//                 "size" : 145125
//               }
//             ],
//             loaded: false
//           }
//           store.commit("content", client );
//           store.dispatch("initClient", id);
//         }
//         return client;
//       }
//     },
//     groupContent: function(state) {
//       return function(id) {
//         var group = store.getters.group(id);
//         var files = [];
//         if(group.loaded) {
//           var loaded = true;
//           for(var c in group.clients) {
//             var client = store.getters.content(group.clients[c]._id);
//             files.push(client);
//             loaded = loaded && client.loaded;
//           }
//         }
//         return { id: id, files: files, loaded: loaded }
//       }
//     }
//   }
// });
//
