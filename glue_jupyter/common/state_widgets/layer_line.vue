<template>
    <div>
        <div>
            <glue-float-field label="line width" suffix="px" :value.sync="linewidth" echo-type="float" />
        </div>
        <div>
            <v-select label="line style" :items="linestyle_items" v-model="linestyle_selected" hide-details />
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">opacity</v-subheader>
            <glue-throttled-slider wait="300" min="0" max="1" step="0.01" :value.sync="alpha" echo-type="float" hide-details />
        </div>
    </div>
</template>
