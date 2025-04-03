<script lang="ts">
  import { Combobox } from '@skeletonlabs/skeleton-svelte';
  
  interface ItemData {
    label: string;
    value: string;
  }

  interface Data {
    name: string;
    id: string;
  }

  interface Props {
    items: Data[];
    label: string;
    placeholder: string;
    name: string;
    value?: string;
  }
  let { items, label, placeholder, name, value = $bindable() }: Props = $props();

  let itemsData: ItemData[] = items.map((item) => ({
    label: item.name,
    value: item.id
  }))

  let selectedCountry = $state([itemsData[0].value]);

  $effect(() => {
    value = selectedCountry[0];
  })
</script>

<input type="hidden" {name} value={selectedCountry[0]} />

<Combobox
  data={itemsData}
  value={selectedCountry}
  onValueChange={(e) => (selectedCountry = e.value)}
  labelClasses="*:text-sm *:font-normal"
  inputGroupClasses="shadow-none focus-within:outline-2 focus-within:outline-primary-500 h-12 bg-white placeholder:text-gray-400 *:shadow-none *:border-none"
  {label}
  {placeholder}
>
  {#snippet item(item)}
    <div class="flex w-full justify-between space-x-2 outline-offset-2">
      <span>{item.label}</span>
    </div>
  {/snippet}
</Combobox>