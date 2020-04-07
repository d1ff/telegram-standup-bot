<template>
    <div>
    <b-table striped hover
             :items="reports"
             :fields="fields">
        <template v-slot:cell(date)="data">
            {{ data.item.date.toDateString() }}
        </template>
    </b-table>
    <b-button @click="loadMore" :disabled="!isLoadMoreEnabled">
        Load more...
    </b-button>
    </div>
</template>
<script lang="ts">
// @ is an alias to /src
import { Component, Prop, Vue } from 'vue-property-decorator';
import Axios from 'axios';
import _ from 'lodash';

let LOGGER_API = process.env.VUE_APP_LOGGER_API_URL;

@Component
export default class UserReports extends Vue {
    @Prop({required: true})
    public user!: string;
    public reports!: any[];
    public fields = ["date", "feel", "yesterday", "today", "block", "absences"];
    public lastId!: string;
    public isLoadMoreEnabled: boolean = true;

    async mounted() {
        let {data} = await Axios.get(
            LOGGER_API+'/reports/'+this.user);
        this.reports = _.map(data, (x) => {
            x['date'] = new Date(x['date']);
            this.lastId = x['_id']['$oid'];
            return x;
        });
    }

    async loadMore() {
        let {data} = await Axios.get(
            LOGGER_API+'/reports/'+this.user+'?start_value='+this.lastId);
        this.reports = _.concat(this.reports, _.map(data, (x) => {
            x['date'] = new Date(x['date']);
            this.lastId = x['_id']['$oid'];
            return x;
        }));
        this.isLoadMoreEnabled = data.length != 0;
    }
}

</script>
