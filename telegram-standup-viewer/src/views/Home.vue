<template>
    <b-tabs >
        <b-tab :title="user" v-for="user in users" :key="user">
            <UserReports :user="user" />
        </b-tab>
    </b-tabs>
</template>

<script lang="ts">
// @ is an alias to /src
import { Component, Vue } from 'vue-property-decorator';
import Axios from 'axios';
import UserReports from '@/components/UserReport.vue'

let LOGGER_API = process.env.VUE_APP_LOGGER_API_URL;

@Component({
    components: {
        'UserReports': UserReports
    }
})
export default class Home extends Vue {
    users = [];

    async mounted() {
        let {data} = await Axios.get(
            LOGGER_API+'/users');
        this.users = data.sort();
    }
}
</script>
