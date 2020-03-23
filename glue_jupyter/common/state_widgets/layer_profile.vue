<template>
    <div>
        <div>
            <v-text-field label="line width" suffix="px" v-model.number="glue_state.linewidth" type="number" hide-details />
        </div>
        <div>
            <v-select label="attribute" :items="attribute_items" v-model="attribute_selected" hide-details />
        </div>
        <div>
            <v-text-field label="vmin" v-model.number="glue_state.v_min" type="number" hide-details />
        </div>
        <div>
            <v-text-field label="vmax" v-model.number="glue_state.v_max" type="number" hide-details />
        </div>
        <div>
            <v-select label="percentile" :items="percentile_items" v-model="percentile_selected" />
        </div>
    </div>
</template>
