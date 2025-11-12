<template>
  <div>
        <v-row dense>
          <v-col cols="5">
            <glue-float-field label="xmin" :value.sync="glue_state.x_min"/>
          </v-col>

          <v-col cols="5">
            <glue-float-field label="xmax" :value.sync="glue_state.x_max"/>
          </v-col>
        </v-row>

        <v-row dense>
          <v-col cols="5">
            <glue-float-field label="ymin" :value.sync="glue_state.y_min"/>
          </v-col>

          <v-col cols="5">
            <glue-float-field label="ymax" :value.sync="glue_state.y_max"/>
          </v-col>
        </v-row>
  </div>
</template>

<script>
    /* `glue_state` is linked to the text-field and `value` will only be updated when it's a valid number
       This means that any formatting such as '1e3' will be kept.
       Only when `value` is changed externally, `glue_state` will be update according to the current `value`.
    */
    module.exports = {
        props: { glue_state: { type: Object, default: () => ({ x_min: 0, x_max: 1, y_min: 0, y_max: 1 }) } },
        watch: {
            glue_state: { handler(value) {
                // when we change the input, we only update value when valid
                // and we emit the change only when we have a valid number
                this.$emit('update:value', value);
            },
              deep: true
            }
            },
    }
</script>
