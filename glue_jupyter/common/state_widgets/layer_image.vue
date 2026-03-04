<template>
    <div>
        <div>
            <v-select label="attribute" :items="attribute_items" v-model="attribute_selected" hide-details class="margin-bottom: 16px" />
        </div>
        <template v-if="has_contour">
            <v-divider class="mt-6"/>
            <div>
                <strong>Contour</strong>
                <v-btn icon @click.stop="glue_state.contour_visible = !glue_state.contour_visible">
                    <v-icon>mdi-eye{{ glue_state.contour_visible ? '' : '-off' }}</v-icon>
                </v-btn>
            </div>
            <v-expand-transition>
                <div v-if="glue_state.contour_visible">
                    <v-btn-toggle density="compact" v-model="glue_state.level_mode" style="margin-right: 8px; margin-top: 8px">

                        <v-tooltip bottom>
                            <template v-slot:activator="{ props }">
                                <v-btn v-bind="props" size="small" value="Linear">
                                    <v-icon>mdi-call-made</v-icon>
                                </v-btn>
                            </template>
                            <span>linear</span>
                        </v-tooltip>

                        <v-tooltip bottom>
                            <template v-slot:activator="{ props }">
                                <v-btn v-bind="props" size="small" value="Custom">
                                    <v-icon>mdi-wrench</v-icon>
                                </v-btn>
                            </template>
                            <span>custom</span>
                        </v-tooltip>
                    </v-btn-toggle>

                    <template v-if="glue_state.level_mode == 'Linear'">
                        <glue-float-field label="contour min" v-model:value="glue_state.c_min" />
                        <glue-float-field label="contour max" v-model:value="glue_state.c_max" />
                        <glue-float-field label="number of contour levels" v-model:value="glue_state.n_levels"/>
                    </template>
                    <v-text-field v-else label="contour levels" v-model="c_levels_txt" :rules="() => c_levels_error !== ''"
                                  :error-messages="c_levels_error !== '' && [c_levels_error]"/>
                </div>
            </v-expand-transition>
            <v-divider class="mt-6"/>
            <div>
                <strong>Bitmap</strong>
                <v-btn icon @click.stop="glue_state.bitmap_visible = !glue_state.bitmap_visible">
                    <v-icon>mdi-eye{{ glue_state.bitmap_visible ? '' : '-off' }}</v-icon>
                </v-btn>
            </div>
        </template>
        <v-expand-transition>
            <div v-if="!has_contour || glue_state.bitmap_visible">
                <div>
                    <div class="slider-label">opacity</div>
                    <glue-throttled-slider wait="300" max="1" step="0.01" v-model:value="glue_state.alpha" hide-details />
                </div>
                <div>
                    <div class="slider-label">contrast</div>
                    <glue-throttled-slider wait="300" max="4" step="0.01" v-model:value="glue_state.contrast" hide-details />
                </div>
                <div>
                    <div class="slider-label">bias</div>
                    <glue-throttled-slider wait="300" max="1" step="0.01" v-model:value="glue_state.bias" hide-details />
                </div>
                <div>
                    <v-select label="stretch" :items="stretch_items" v-model="stretch_selected" hide-details />
                </div>
                <div>
                    <v-select label="percentile" :items="percentile_items" v-model="percentile_selected" hide-details />
                </div>
                <div>
                    <glue-float-field label="min" v-model:value="glue_state.v_min" />
                </div>
                <div>
                    <glue-float-field label="max" v-model:value="glue_state.v_max" />
                </div>
                <div v-if="color_mode === 'Colormaps'">
                    <v-select label="colormap" :items="colormap_items" :model-value="glue_state.cmap" @update:modelValue="set_colormap" />
                </div>
            </div>
        </v-expand-transition>
    </div>
</template>
<script>
    modules.export = {
        methods: {
            /* TODO: use @change with debounce instead of @end */
            setAlpha(value) {
                this.glue_state.alpha = value;
            },
            setContrast(value) {
                this.glue_state.contrast = value;
            },
            setBias(value) {
                this.glue_state.bias = value;
            },
        },
    }
</script>
<style id="layer_image">
    .slider-label {
        font-size: 12px;
        height: 16px;
    }
</style>
