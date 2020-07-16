<template>
    <div>
        <div>
            <glue-float-field label="line width" suffix="px" :value.sync="glue_state.linewidth" />
        </div>
        <div>
            <v-select label="attribute" :items="attribute_items" v-model="attribute_selected" hide-details />
        </div>
        <div>
            <glue-float-field label="vmin" :value.sync="glue_state.v_min" />
        </div>
        <div>
            <glue-float-field label="vmax" :value.sync="glue_state.v_max" />
        </div>
        <div>
            <v-select label="percentile" :items="percentile_items" v-model="percentile_selected" />
        </div>
    </div>
</template>
