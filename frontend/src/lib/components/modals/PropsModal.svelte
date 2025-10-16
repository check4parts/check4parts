<script lang="ts">
	import { enhance } from '$app/forms';
	import { Dialog } from 'bits-ui';
	import type { ActionData } from '../../../routes/home/settings/suppliers/api/[id]/$types';
	import InputTextField from '$lib/components/inputs/edit-modal/InputTextField.svelte';
	import InputTextareaField from '$lib/components/inputs/edit-modal/InputTextareaField.svelte';

	interface Props {
		openState: boolean;
		modalClose?: () => void;
		editPage: boolean;
		data: {
			title: string;
			value?: string;
			placeholder: string;
			type: string;
			name: string;
		}[];
		form?: ActionData;
		id: string;
		action?: string;
		title?: string;
	}

	let {
		openState = $bindable(false),
		modalClose = () => {
			openState = false;
		},
		editPage = $bindable(),
		form = $bindable(),
		data = $bindable(),
		action = '?/edit',
		title = 'Редагування деталей',
		id
	}: Props = $props();

	let saving = $state(false);
	$effect(() => {
		if (openState) {
			saving = false;
		}
	});
</script>

<Dialog.Root bind:open={openState}>
	<Dialog.Portal>
		<Dialog.Overlay
			class="data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/80"
		/>
		<Dialog.Content
			class="fixed left-[50%] top-[50%] z-50 h-fit w-1/2 translate-x-[-50%] translate-y-[-50%] rounded-xl bg-white p-4"
		>
			<div class="flex w-full justify-end">
				<button type="button" class="preset-tonal-surface-100" onclick={modalClose}>
					<img src="/close-icon.svg" alt="close" class="size-4" />
				</button>
			</div>
			<Dialog.Title
				class="з-4 flex w-full items-center justify-end text-lg font-semibold tracking-tight"
			>
				<h4 class="h5 w-full text-center">{title}</h4>
			</Dialog.Title>
			<Dialog.Description class="p-4">
				<form
					class="flex flex-col gap-5 px-10"
					method="POST"
					use:enhance={() => {
						return async ({ update }) => {
							update({ reset: false });
						};
					}}
					onsubmit={() => (saving = true)}
					{action}
				>
					<input type="hidden" name="id" value={id} />
					<input type="hidden" name="data_props" value={JSON.stringify(data)} />
					{#each data as item}
						{#if item.type === 'text'}
							<InputTextField
								lable={item.title}
								name={item.name}
								placeholder={item.placeholder}
								defaultValue={item.value ?? ''}
								value={item.value ?? ''}
							/>
						{/if}
					{/each}
					{#each data as item}
						{#if item.type === 'textarea'}
							<InputTextareaField
								lable={item.title}
								name={item.name}
								placeholder={item.placeholder}
								defaultValue={item.value}
							/>
						{/if}
					{/each}
					<div class="flex justify-end gap-4">
						<button
							type="button"
							class="btn preset-outlined-primary-950-50 text-xl"
							onclick={modalClose}>Скасувати</button
						>
						<button
							type="submit"
							class="btn preset-filled-primary-950-50 text-xl"
							disabled={saving}
						>
							{#if saving}
								Збереження...
							{:else}
								Зберегти
							{/if}
						</button>
					</div>
				</form>
			</Dialog.Description>
			<Dialog.Close />
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>
