<template>
  <div>
  <v-row no-gutters>
    <v-col cols="6">
      <glue-float-field class="mr-1" label="xmin" :value.sync="glue_state.x_min" />
    </v-col>
    <v-col  cols="6">
      <glue-float-field class="ml-1" label="xmax" :value.sync="glue_state.x_max" />
    </v-col>
  </v-row>
  <v-row no-gutters>
    <v-col cols="6">
      <glue-float-field class="mr-1" label="ymin" :value.sync="glue_state.y_min" />
    </v-col>
    <v-col cols="6">
      <glue-float-field class="ml-1" label="ymax" :value.sync="glue_state.y_max" />
    </v-col>
  </v-row>
  </div>
</template>
