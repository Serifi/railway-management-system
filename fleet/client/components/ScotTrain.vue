<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div class="flex flex-col space-y-1 col-span-2">
      <label for="name">{{ $t('name') }}</label>
      <InputText id="name" v-model="train.name" :placeholder="$t('textPlaceholder')" :disabled="isDisabled('name')" />
    </div>

    <div class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="railcar">{{ $t('railcar') }}</label>
      <Select
          id="railcar"
          v-model="train.railcarID"
          :options="railcars"
          :optionLabel="formatRailcarOption"
          optionValue="carriageID"
          :placeholder="$t('selectPlaceholder')"
          :disabled="isDisabled('railcarID')"
      />
    </div>

    <div class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="passengerCars">{{ $t('passengerCar') }}</label>
      <MultiSelect
          id="passengerCars"
          v-model="train.passengerCarIDs"
          :options="passengerCars"
          :optionLabel="formatPassengerCarOption"
          optionValue="carriageID"
          :placeholder="$t('selectPlaceholder')"
          :disabled="isDisabled('passengerCarIDs')"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useTrainStore } from '@/stores/train'
import {useI18n} from "vue-i18n"

const { t } = useI18n()
const emits = defineEmits(['update:train'])
const props = defineProps({
  train: {
    type: Object,
    default: () => ({
      name: '',
      railcarID: null,
      passengerCarIDs: []
    })
  },
  disabledFields: {
    type: Array,
    default: () => []
  }
})

const train = ref({ ...props.train })
const trainStore = useTrainStore()
const railcars = computed(() => trainStore.railcars)
const passengerCars = computed(() => trainStore.passengerCars)

const isDisabled = (field) => props.disabledFields.includes(field)

const formatRailcarOption = (option) => {
  if (!option) return ''
  return `ID: ${option.carriageID} - ${t('maxTractiveForce')}: ${option.maxTractiveForce}kN`
}

const formatPassengerCarOption = (option) => {
  if (!option) return ''
  return `ID: ${option.carriageID} - ${t('maxWeight')}: ${option.maxWeight}kg - ${t('numberOfSeats')}: ${option.numberOfSeats}`
}

watch(
    [
      () => train.value.name,
      () => train.value.railcarID,
      () => train.value.passengerCarIDs
    ],
    ([name, railcarID, passengerCarIDs]) => {
      let allFieldsFilled = false

      if (name && railcarID && passengerCarIDs.length > 0) {
        allFieldsFilled = true
      }

      emits('update:train', allFieldsFilled ? train.value : null)
    },
    { deep: true }
)
</script>