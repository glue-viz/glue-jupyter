<template>
    <v-btn-toggle :model-value="active_tool_id" class="transparent glue-toolbar" style="overflow: visible;">
        <template v-for="[id, data] of Object.entries(tools_data)" :key="id">
            <v-tooltip location="bottom">
                <template v-slot:activator="{ props: tooltipProps }">
                    <v-menu v-if="data.subtools">
                        <template v-slot:activator="{ props: menuProps }">
                            <v-btn icon variant="text" :value="id" style="position: relative;" v-bind="tooltipProps" v-bind="menuProps">
                                <img :src="data.img" width="20"/>
                            </v-btn>
                        </template>
                        <v-list style="overflow-x: hidden" select-strategy="single-leaf"
                                :selected="active_tool_id !== null ? [active_tool_id] : []"
                                @update:selected="selected => {
                                  if (!(selected || selected.length > 0)) {
                                      active_tool_id = null;
                                  } else {
                                      active_tool_id = selected.includes(active_tool_id) ? null : selected[0];
                                  }
                                }">
                            <v-list-item v-for="[subtool_id, subtool_data] in Object.entries(data.subtools)" :key="subtool_data.tool_id" :value="subtool_id">
                                <template #prepend>
                                    <v-avatar size="24" tile><v-img :src="subtool_data.img"></v-img></v-avatar>
                                </template>
                                <template #title>
                                    <span class="text-body-2 text-important">{{ subtool_data.tooltip }}</span>
                                </template>
                            </v-list-item>
                        </v-list>
                    </v-menu>
                    <v-btn v-else icon variant="text" :value="id" style="position: relative;" v-bind="tooltipProps"
                            @click="active_tool_id = id">
                        <img :src="data.img" width="20"/>
                    </v-btn>
                </template>
                {{ data.tooltip }}
            </v-tooltip>
        </template>
    </v-btn-toggle>
</template>
