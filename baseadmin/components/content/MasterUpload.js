var MasterContent = Vue.component( "MasterContent", {
  template : `
<div>
  <h1>Upload Content</h1>
    <form id="uploadForm" enctype="multipart/form-data">
      <vue-form-generator :schema="schema" :options="formOptions"></vue-form-generator>
      progress: <progress></progress>
    </form>
  
  <h1>Available Content</h1>
  <v-data-table
    v-if="files"
    :headers="headers"
    :items="files"
    hide-actions
    class="elevation-1"
  >
    <template slot="items" slot-scope="props">
      <td>{{ props.item.name }}</td>
      <td class="text-xs-right">{{ props.item.size }}</td>
      <td width="1%">
        <v-btn color="red" fab small dark @click="deleteMasterFile(props.item.name)">
          <v-icon>delete</v-icon>
        </v-btn>
      </td>
    </template>
  </v-data-table>
</div>`,
  computed: {
    files: function() {
      return store.getters.files;
    }
  },
  methods: {
    deleteMasterFile: function(name) {
      var state = this;
      perform("removeFile", name, function(result) {
        if("success" in result && result.success) {
          store.commit("removedFile", name);
        } else  {
          app.$notify({
            group: "notifications",
            title: "Failed to remove file...",
            text:  "message" in result ? result.message : "unknown reason",
            type:  "warn",
            duration: 10000
          });
        }
      });
    }
  },
  data: function() {
    return {
      headers: [
        {
          text    : "Name",
          align   : "left",
          sortable: true,
          value   : "name"
        },
        {
          text    : "Size",
          align   : "right",
          value   : "size"
        },
        {
          text    : "",
          align   : "right",
          value   : "size"
        }
      ],
      schema: {
        fields: [
          {
            type: "upload",
            inputName: 'filename',
            onChanged: function(model, schema, event, instance) {
              $.ajax({
                url: "/api/content",
                type: "POST",
                data: new FormData($("#uploadForm")[0]),
                cache: false,
                contentType: false,
                processData: false,
                success: function(response) {
                  $('progress').attr({ value: 0, max: 0 });
                  store.commit("newFile", response);
                },
                error: function(response) {
                  app.$notify({
                    group: "notifications",
                    title: "File upload failed...",
                    text:  response.responseJSON.message,
                    type:  "warn",
                    duration: 10000
                  });
                  $('progress').attr({ value: 0, max: 0 });
                },
                xhr: function() {
                  var myXhr = $.ajaxSettings.xhr();
                  if(myXhr.upload) {
                    myXhr.upload.addEventListener("progress", function(e) {
                      if (e.lengthComputable) {
                        $('progress').attr({
                          value: e.loaded,
                          max:   e.total,
                        });
                      }
                    } , false);
                  }
                  return myXhr;
                }
             });
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

var masterSection = app.sections.find(function(item) {
  return "group" in item && item.group && item.text == "Master";
});
if(! masterSection ) {
  masterSection = {
    group      : true,
    icon       : "home",
    text       : "Master",
    subsections: []
  }
  app.sections.push(masterSection);
}

masterSection.subsections.push({
  icon : "perm_media",
  text : "Content",
  path : "/content"
});

router.addRoutes([{
  path      : "/content",
  component : MasterContent
}]);

store.registerModule("MasterContent", {
  state: {
    files: []
  },
  mutations: {
    files: function(state, files) {
      state.files = files;
    },
    newFile: function(state, file){
      state.files.push(file);
    },
    removedFile: function(state, file) {
      state.files = state.files.filter(function(item) {
        return item.name != file;
      });
    }
  },
  getters: {
    files: function(state) {
      return state.files;
    }
  }
});

state_handlers.push(function(state) {
  store.commit("files", state.files);
});
