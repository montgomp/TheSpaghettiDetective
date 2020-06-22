<template>
  <div class="col-sm-12 col-md-6 col-lg-4 pt-3">
    <div class="card vld-parent">
      <loading :active="videoDownloading" :is-full-page="true"></loading>
      <div class="card-header">
        <div>
          <b-form-checkbox
            v-model="selected"
            @change="onSelectedChange"
            size="lg"
            class="text-decoration-none"
          ></b-form-checkbox>
        </div>
        <b-form-radio-group
          v-model="selectedCardView"
          buttons
          button-variant="outline-primary"
          name="radio-btn-outline"
        >
          <b-form-radio value="detective" class="square-btn" :disabled="!print.has_detective_view">
            <img
              class="seg-control-icon"
              :src="require('../../../app/static/img/logo-square-inverted.png')"
            />
          </b-form-radio>
          <b-form-radio value="info" class="square-btn">
            <img
              class="seg-control-icon"
              :src="require('../../../app/static/img/info-inverted.png')"
            />
          </b-form-radio>
        </b-form-radio-group>

        <div class="dropdown">
          <button
            class="btn icon-btn"
            type="button"
            id="dropdownMenuButton"
            data-toggle="dropdown"
            aria-haspopup="true"
            aria-label="Controls"
          >
            <i class="fas fa-ellipsis-v"></i>
          </button>
          <div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenuButton">
            <a class="dropdown-item" v-if="this.print.video_url" @click="downloadVideo(false)">
              <i class="fas fa-download"></i>Download Original Time-lapse
            </a>
            <a
              class="dropdown-item"
              v-if="this.print.tagged_video_url"
              @click="downloadVideo(true)"
            >
              <i class="fas fa-download"></i>Download Detective Time-lapse
            </a>
            <div class="dropdown-divider"></div>
            <a class="dropdown-item text-danger" @click="deleteVideo">
              <i class="fas fa-trash-alt"></i>Delete
            </a>
          </div>
        </div>
      </div>
      <div v-show="cardView == 'info'">
        <video-box :videoUrl="print.video_url" :posterUrl="print.poster_url" />
        <div class="card-body">
          <div class="container">
            <div class="row">
              <div class="text-muted col-4">File:</div>
              <div class="col-8">{{ print.filename }}</div>
            </div>
            <div class="row">
              <div class="text-muted col-4">{{ wasTimelapseUploaded ? "Uploaded" : "Printed" }}:</div>
              <div
                class="col-8"
              >{{ wasTimelapseUploaded ? print.uploaded_at.fromNow() : print.ended_at.fromNow() }} {{ endStatus }}</div>
            </div>
            <div class="row" v-if="!wasTimelapseUploaded">
              <div class="text-muted col-4">Duration:</div>
              <div class="col-8">{{ duration.humanize() }}</div>
            </div>
          </div>
        </div>
      </div>
      <div v-show="cardView == 'detective' && print.has_detective_view">
        <video-box
          :videoUrl="print.tagged_video_url"
          :posterUrl="print.poster_url"
          @timeupdate="onTimeUpdate"
        />
        <gauge :predictionJsonUrl="print.prediction_json_url" :currentPosition="currentPosition" />
        <div class="feedback-section">
          <div class="text-center py-2 px-3">
            <div
              class="lead"
              :class="[print.alerted_at ? 'text-danger' : 'text-success', ]"
            >{{ print.alerted_at ? 'The Detective found spaghetti' : 'The Detective found nothing fishy' }}</div>
            <div class="py-2">
              Did she get it right?
              <b-button
                :variant="thumbedUp ? 'primary' : 'outline'"
                @click="onThumbUpClick"
                class="mx-2 btn-sm"
              >
                <i class="fas fa-thumbs-up"></i>
              </b-button>
              <b-button
                :variant="thumbedDown ? 'primary' : 'outline'"
                @click="onThumbDownClick"
                class="mx-2 btn-sm"
              >
                <i class="fas fa-thumbs-down"></i>
              </b-button>
            </div>
            <transition name="bounce">
              <div v-if="focusedFeedbackEligible" class="pt-2">
                <a
                  role="button"
                  class="btn btn-sm btn-outline-primary px-4"
                  :href="focusedFeedbackLink"
                >
                  F
                  <i class="fas fa-search focused-feedback-icon"></i>CUSED FEEDBACK
                  <img
                    class="seg-control-icon ml-1"
                    :src="require('../../../app/static/img/detective-hour-2-primary.png')"
                  />
                </a>
              </div>
            </transition>
          </div>
          <div class="text-muted py-2 px-3 help-text">
            <small v-if="!focusedFeedbackEligible">
              Every time you give The Detective feedback by telling her if she got it right, you help her get better at detecting spaghetti.
              <a
                href="https://www.thespaghettidetective.com/docs/how-does-credits-work/"
              >Learn more!</a>
            </small>
            <small
              v-if="focusedFeedbackEligible"
            >With Focused Feedback, you can tell The Detective exactly where she got it wrong. This is the most effective way to help her improve. You will earn 2 Detective Hours once you finnish the Focused Feedback.</small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import fileDownload from "js-file-download";
import moment from "moment";
// TODO: this should be configured as global. But for some reason it doesn't work.
import Loading from "vue-loading-overlay";
import "vue-loading-overlay/dist/vue-loading.css";

import url from "../lib/url";
import VideoBox from "../common/VideoBox";
import Gauge from "../common/Gauge";

export default {
  name: "PrintCard",

  components: {
    Loading,
    VideoBox,
    Gauge
  },

  data: () => {
    return {
      videoDownloading: false,
      currentPosition: 0,
      selectedCardView: "detective",
      selected: false,
      localOverwrite: null
    };
  },

  props: {
    print: Object
  },

  computed: {
    wasTimelapseUploaded() {
      return this.print.uploaded_at !== null;
    },

    endStatus() {
      return this.print.cancelled_at ? "(Cancelled)" : "";
    },

    duration() {
      return moment.duration(this.print.ended_at.diff(this.print.started_at));
    },

    cardView() {
      return this.print.has_detective_view ? this.selectedCardView : "info";
    },

    thumbedUp() {
      if (this.localOverwrite) {
        return this.localOverwrite === "thumbedUp";
      }
      if (!this.print.alert_overwrite) {
        return false;
      }
      return (
        this.print.has_alerts ^ (this.print.alert_overwrite === "NOT_FAILED")
      );
    },

    thumbedDown() {
      if (this.localOverwrite) {
        return this.localOverwrite === "thumbedDown";
      }
      if (!this.print.alert_overwrite) {
        return false;
      }
      return this.print.has_alerts ^ (this.print.alert_overwrite === "FAILED");
    },

    focusedFeedbackEligible() {
      return this.print.printshotfeedback_set.length > 0 && this.thumbedDown;
    },

    focusedFeedbackLink() {
      return `/prints/shot-feedback/${this.print.id}/`;
    }
  },

  methods: {
    onTimeUpdate(currentPosition) {
      this.currentPosition = currentPosition;
    },

    onSelectedChange() {
      this.$emit("selectedChange", this.print.id, !this.selected); // this method is called before this.selected is flipped. So need to inverse it before passing it event listener
    },

    downloadVideo(detectiveVideo) {
      this.videoDownloading = true;
      const x = new XMLHttpRequest();
      const filename = `${this.print.filename}${
        detectiveVideo ? "_detective_view" : ""
      }.mp4`;
      x.open(
        "GET",
        detectiveVideo ? this.print.tagged_video_url : this.print.video_url,
        true
      );
      x.responseType = "blob";
      x.onload = e => {
        fileDownload(e.target.response, filename);
        this.videoDownloading = false;
      };
      x.send();
    },

    deleteVideo() {
      axios.delete(url.print(this.print.id)).then(() => {
        this.$emit("printDeleted");
      });
    },

    onThumbUpClick() {
      this.localOverwrite = "thumbedUp";
      this.alertOverwrite(this.print.has_alerts ? "FAILED" : "NOT_FAILED");
    },

    onThumbDownClick() {
      this.localOverwrite = "thumbedDown";
      this.alertOverwrite(this.print.has_alerts ? "NOT_FAILED" : "FAILED");
    },

    alertOverwrite(value) {
      axios.post(url.printAlertOverwrite(this.print.id), { value });
    }
  }
};
</script>

<style lang="sass" scoped>
@import "../main/main.sass"

.card-header
  display: flex
  flex-flow: row nowrap
  justify-content: space-between
  align-items: center

.seg-control-icon
  height: 1.2rem

.feedback-section
  background-color: $color-bg-dark

.bounce-enter-active
  animation: bounce-in .5s

.bounce-leave-active
  animation: bounce-in .5s reverse

@keyframes bounce-in
  0%
    transform: scale(0)
  50%
    transform: scale(1.5)
  100%
    transform: scale(1)

.help-text
  line-height: 1.2
</style>