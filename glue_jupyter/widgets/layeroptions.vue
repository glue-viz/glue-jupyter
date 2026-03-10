<template>
    <div class="glue-layer-options">
        <div>
            <v-select
                    :items="layers"
                    item-title="label"
                    item-value="index"
                    v-model="selected"
                    label="Layer"
                    hide-details
            >
                <template v-slot:selection="{ item }">
                    <div class="single-line">
                        <v-menu v-model="color_menu_open">
                            <template v-slot:activator="{ props }">
                                <span class="glue-color-menu"
                                      v-bind="props"
                                      :style="`background:${item.raw.color}`"
                                      @click.stop
                                >&nbsp;</span>
                            </template>
                            <div @click.stop="" style="text-align: end; background-color: white">
                                <v-btn icon @click="color_menu_open = false">
                                    <v-icon>mdi-close</v-icon>
                                </v-btn>
                                <v-color-picker v-model="item.raw.color"></v-color-picker>
                            </div>
                        </v-menu>
                        <v-btn icon @click.stop="item.raw.visible = !item.raw.visible">
                            <v-icon>mdi-eye{{ item.raw.visible ? '' : '-off' }}</v-icon>
                        </v-btn>
                        {{ item.raw.label }}
                    </div>
                </template>
                <template v-slot:item="{ props, item }">
                    <div class="single-line" v-bind="props">
                        <span class="glue-color-menu"
                              :style="`background:${item.raw.color}`"
                        >&nbsp;</span>
                        <v-icon style="padding: 0 4px" @click.stop="item.raw.visible = !item.raw.visible">
                            mdi-eye{{ item.raw.visible ? '' : '-off' }}
                        </v-icon>
                        {{ item.raw.label }}
                    </div>
                </template>
            </v-select>
        </div>
        <div>
            <jupyter-widget v-if="layers && current_panel" :widget="current_panel"></jupyter-widget>
        </div>
    </div>
</template>

<style id="glue-layeroptions">
    .glue-layer-options {
        width: 100%;
    }

    .glue-color-menu {
        font-size: 16px;
        padding-left: 16px;
        border: 2px solid rgba(0,0,0,0.54);
    }

    .single-line {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        width: 100%;
    }
</style>
