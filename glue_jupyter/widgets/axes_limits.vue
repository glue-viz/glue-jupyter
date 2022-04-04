<template>
  <v-row>
    <v-col cols=6>
      <glue-float-field label="xmin" :value.sync="glue_state.x_min" />
    </v-col cols=6>
    <v-col>
      <glue-float-field label="xmax" :value.sync="glue_state.x_max" />
    </v-col>
  </v-row>
  <v-row>
    <v-col cols=6>
      <glue-float-field label="ymin" :value.sync="glue_state.y_min" />
    </v-col>
    <v-col cols=6>
      <glue-float-field label="ymax" :value.sync="glue_state.y_max" />
    </v-col>
  </v-row>
</template>
