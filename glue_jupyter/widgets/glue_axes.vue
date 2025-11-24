<template>
  <div>
        <v-row dense>
          <v-col cols="5">
            <glue-float-field label="xmin" :value.sync="value.x_min"/>
          </v-col>

          <v-col cols="5">
            <glue-float-field label="xmax" :value.sync="value.x_max"/>
          </v-col>
        </v-row>

        <v-row dense>
          <v-col cols="5">
            <glue-float-field label="ymin" :value.sync="value.y_min"/>
          </v-col>

          <v-col cols="5">
            <glue-float-field label="ymax" :value.sync="value.y_max"/>
          </v-col>
        </v-row>
  </div>
  <div>
      <v-text-field :label="x-label" :value.sync="glue_state.x_axislabel"/>
      <v-text-field :label="y-label" :value.sync="glue_state.y_axislabel"/>
  </div>
</template>

<script>
    /* `glue_state` is linked to the text-field and `value` will only be updated when it's a valid number
       This means that any formatting such as '1e3' will be kept.
       Only when `value` is changed externally, `glue_state` will be update according to the current `value`.
    */
    module.exports = {
        props: { value: { type: Object, default: () => ({ x_min: 0, x_max: 1, y_min: 0, y_max: 1 }) } },
    }
</script>
