<template>
    <div>
        <div>
            <glue-float-field label="line width" suffix="px" v-model:value="glue_state.linewidth" />
        </div>
        <div>
            <v-select label="attribute" :items="attribute_items" v-model="attribute_selected" hide-details />
        </div>
        <div>
            <div class="slider-label">opacity</div>
            <glue-throttled-slider wait="300" min="0" max="1" step="0.01" v-model:value="glue_state.alpha" hide-details />
        </div>
        <div>
            <v-switch label="Plot as steps" v-model="as_steps" />
        </div>
    </div>
</template>
<style>
    .slider-label {
        font-size: 12px;
        height: 16px;
        margin-top: 6px;
    }
</style>
