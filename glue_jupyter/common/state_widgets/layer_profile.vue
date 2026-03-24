<template>
    <div>
        <div>
            <glue-float-field label="line width" suffix="px" :value.sync="linewidth" echo-type="number" />
        </div>
        <div>
            <v-select label="attribute" :items="attribute_items" v-model="attribute_selected" hide-details />
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">opacity</v-subheader>
            <glue-throttled-slider wait="300" min="0" max="1" step="0.01" :value.sync="alpha" echo-type="number" hide-details />
        </div>
        <div>
            <v-switch label="Plot as steps" v-model="as_steps" />
        </div>
    </div>
</template>
