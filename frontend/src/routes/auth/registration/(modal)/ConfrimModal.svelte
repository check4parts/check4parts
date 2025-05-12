<script lang="ts">
	import { goto } from '$app/navigation';
	import { Dialog } from 'bits-ui';

	interface Props {
		open?: any;
		modalClose?: () => void;
	}

	let {
		open = $bindable(),
		modalClose = () => {
			open = false;
		}
	}: Props = $props();
</script>

<Dialog.Root bind:open>
	<Dialog.Portal>
		<Dialog.Overlay
			class="data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/80"
		/>
		<Dialog.Content
			class="fixed top-[50%] left-[50%] z-50 w-fit max-w-1/4 min-w-1/4 translate-x-[-50%] translate-y-[-50%] rounded-xl bg-white p-5"
		>
			<div class="absolute top-3 right-4">
				<button type="button" class="preset-tonal-surface-100" onclick={modalClose}>
					<img src="/close-icon.svg" alt="close" class="size-4" />
				</button>
			</div>
			<Dialog.Title
				class="flex w-full items-center justify-end p-4 text-lg font-semibold tracking-tight"
			>
				<h4 class="h5 w-full text-left">Заявку на реєстрацію надіслано!</h4>
			</Dialog.Title>
			<Dialog.Description>
				<p class="text-surface-500 p-4 text-left">
					Ваші дані успішно передано на перевірку. Після підтвердження реєстрації ви отримаєте лист
					із логіном та паролем на вказану електронну адресу.
					<br />
					<br />
					Дякуємо, що приєднуєтеся до нашої платформи!
				</p>
				<div class="flex h-fit items-center justify-end gap-3">
					<button
						type="button"
						class="btn preset-filled bg-primary-950-50 font-bold"
						onclick={() => {
							modalClose;
							goto('/auth/login');
							}}>Закрити</button
					>
				</div>
			</Dialog.Description>
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>
