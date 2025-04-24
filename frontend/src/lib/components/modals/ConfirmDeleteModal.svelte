<script lang="ts">
	import { Dialog } from 'bits-ui';

	interface Props {
		open?: any;
		modalClose?: () => void;
		title: string;
		message: string;
		action: string;
		itemId: string;
	}

	let {
		open = $bindable(),
		modalClose = () => {
			open = false;
		},
		title,
		message,
		action,
		itemId
	}: Props = $props();
</script>

<Dialog.Root bind:open>
	<Dialog.Portal>
		<Dialog.Overlay
			class="data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/80"
		/>
		<Dialog.Content
			class="fixed top-[50%] left-[50%] z-50 w-fit max-w-1/2 min-w-1/3 translate-x-[-50%] translate-y-[-50%] rounded-xl bg-white p-5"
		>
			<div class="absolute top-3 right-4">
				<button type="button" class="preset-tonal-surface-100" onclick={modalClose}>
					<img src="/close-icon.svg" alt="close" class="size-4" />
				</button>
			</div>
			<Dialog.Title
				class="flex w-full items-center justify-end p-4 text-lg font-semibold tracking-tight"
			>
				<h4 class="h5 w-full text-center">
					{title}
				</h4>
			</Dialog.Title>
			<Dialog.Description>
				<p class="text-surface-500 text-center">
					{message}
				</p>
				<form method="POST" {action} class="mt-5">
					<input type="hidden" name="id" value={itemId} />
					<div class="flex h-fit items-center justify-end gap-3">
						<button
							type="button"
							class="btn preset-outlined-primary-950-50 font-bold"
							onclick={modalClose}>Скасувати</button
						>
						<button type="submit" class="btn preset-filled-error-700-300 font-bold">Видалити</button
						>
					</div>
				</form>
			</Dialog.Description>
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>
