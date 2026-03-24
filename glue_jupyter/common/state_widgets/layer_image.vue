<template>
    <div>
        <div>
            <v-select label="attribute" :items="attribute_items" v-model="attribute_selected" hide-details class="margin-bottom: 16px" />
        </div>
        <template v-if="has_contour">
            <v-divider class="mt-6"/>
            <div>
                <strong>Contour</strong>
                <v-btn icon @click.stop="contour_visible = !contour_visible">
                    <v-icon>mdi-eye{{ contour_visible ? '' : '-off' }}</v-icon>
                </v-btn>
            </div>
            <v-expand-transition>
                <div v-if="contour_visible">
                    <v-btn-toggle dense v-model="level_mode" echo-type="text" style="margin-right: 8px; margin-top: 8px">

                        <v-tooltip bottom>
                            <template v-slot:activator="{ on }">
                                <v-btn v-on="on" small value="Linear">
                                    <v-icon>mdi-call-made</v-icon>
                                </v-btn>
                            </template>
                            <span>linear</span>
                        </v-tooltip>

                        <v-tooltip bottom>
                            <template v-slot:activator="{ on }">
                                <v-btn v-on="on" small value="Custom">
                                    <v-icon>mdi-wrench</v-icon>
                                </v-btn>
                            </template>
                            <span>custom</span>
                        </v-tooltip>
                    </v-btn-toggle>

                    <template v-if="level_mode == 'Linear'">
                        <glue-float-field label="contour min" :value.sync="c_min" echo-type="value" />
                        <glue-float-field label="contour max" :value.sync="c_max" echo-type="value" />
                        <glue-float-field label="number of contour levels" :value.sync="n_levels" echo-type="value" />
                    </template>
                    <v-text-field v-else label="contour levels" v-model="c_levels_txt" :rules="() => c_levels_error !== ''"
                                  :error-messages="c_levels_error !== '' && [c_levels_error]"/>
                </div>
            </v-expand-transition>
            <v-divider class="mt-6"/>
            <div>
                <strong>Bitmap</strong>
                <v-btn icon @click.stop="bitmap_visible = !bitmap_visible">
                    <v-icon>mdi-eye{{ bitmap_visible ? '' : '-off' }}</v-icon>
                </v-btn>
            </div>
        </template>
        <v-expand-transition>
            <div v-if="!has_contour || bitmap_visible">
                <div>
                    <v-subheader class="pl-0 slider-label">opacity</v-subheader>
                    <glue-throttled-slider wait="300" max="1" step="0.01" :value.sync="alpha" echo-type="value" hide-details />
                </div>
                <div>
                    <v-subheader class="pl-0 slider-label">contrast</v-subheader>
                    <glue-throttled-slider wait="300" max="4" step="0.01" :value.sync="contrast" echo-type="value" hide-details />
                </div>
                <div>
                    <v-subheader class="pl-0 slider-label">bias</v-subheader>
                    <glue-throttled-slider wait="300" max="1" step="0.01" :value.sync="bias" echo-type="value" hide-details />
                </div>
                <div>
                    <v-select label="stretch" :items="stretch_items" v-model="stretch_selected" hide-details />
                </div>
                <div>
                    <v-select label="percentile" :items="percentile_items" v-model="percentile_selected" hide-details />
                </div>
                <div>
                    <glue-float-field label="min" :value.sync="v_min" echo-type="value" />
                </div>
                <div>
                    <glue-float-field label="max" :value.sync="v_max" echo-type="value" />
                </div>
                <div v-if="color_mode === 'Colormaps'">
                    <v-select label="colormap" :items="cmap_items" v-model="cmap" />
                </div>
            </div>
        </v-expand-transition>
    </div>
</template>
<script>
</script>
<style id="layer_image">
    .v-subheader.slider-label {
        font-size: 12px;
        height: 16px;
    }
</style>
