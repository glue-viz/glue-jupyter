<template>
    <div>
        <div>
            <v-select :items="x_att_items" label="x axis" v-model="x_att_selected"/>
        </div>
        <div>
            <v-text-field type="number" step="1" label="number of bins" v-model="hist_n_bin" />
        </div>
        <div>
            <glue-float-field label="x-min" :value.sync="hist_x_min" echo-type="number" />
        </div>
        <div>
            <glue-float-field label="x-max" :value.sync="hist_x_max" echo-type="number" />
        </div>
        <div>
            <v-toolbar density="compact" >
                  <v-tooltip>
                    <template v-slot:activator="{ on }">
                         <v-btn v-on="on" size="x-small" value="normalize">
                             <v-icon>unfold_more</v-icon>
                         </v-btn>
                     </template>
                    <span>normalize</span>
                  </v-tooltip>
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on }">
                        <v-btn v-on="on" size="x-small" value="cumulative">
                            <v-icon>trending_up</v-icon>
                        </v-btn>
                    </template>
                    <span>cumulative</span>
                  </v-tooltip>

                  <v-btn variant="outlined" size="x-small" @click="bins_to_axes">
                      Fit Bins to Axes
                  </v-btn>
            </v-toolbar>
        </div>
        <v-switch v-model="show_axes" label="Show axes" hide-details/>
    </div>
</template>
<script>
    module.exports = {
        computed: {
            modeSet() {
                return [this.normalize && 'normalize', this.cumulative && 'cumulative']
            }
        },
        methods: {
            modeSetChange(v) {
                this.normalize = v.includes('normalize');
                this.cumulative = v.includes('cumulative');
            }
        }
    }
</script>
