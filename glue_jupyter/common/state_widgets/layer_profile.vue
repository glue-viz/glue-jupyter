<template>
    <div>
        <div>
            <v-select label="display" :items="display_mode_items" v-model="display_mode_selected" hide-details />
        </div>
        <div>
            <glue-float-field label="line width" suffix="px" :value.sync="linewidth" echo-type="float" />
        </div>
        <div v-if="display_mode_selected !== 'Vertical lines'">
            <v-select label="attribute" :items="attribute_items" v-model="attribute_selected" hide-details />
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">opacity</v-subheader>
            <glue-throttled-slider wait="300" min="0" max="1" step="0.01" :value.sync="alpha" echo-type="float" hide-details />
        </div>
        <div v-if="display_mode_selected !== 'Vertical lines'">
            <v-switch label="Plot as steps" v-model="as_steps" />
        </div>
    </div>
</template>
