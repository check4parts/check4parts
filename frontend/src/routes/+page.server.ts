import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';
import {
	EMAILJS_SERVICE_ID,
	EMAILJS_TEMPLATE_ID,
	EMAILJS_PUBLIC_KEY,
	EMAILJS_PRIVATE_KEY
} from '$env/static/private';

export const actions: Actions = {
	sendEmail: async ({ request }) => {
		const formData = await request.formData();
		const name = formData.get('name') as string;
		const email = formData.get('email') as string;
		const message = formData.get('message') as string;

		if (!name || !email || !message) {
			return fail(400, { error: 'Будь ласка, заповніть усі поля.', name, email, message });
		}

		const data = {
			service_id: EMAILJS_SERVICE_ID,
			template_id: EMAILJS_TEMPLATE_ID,
			user_id: EMAILJS_PUBLIC_KEY,
			accessToken: EMAILJS_PRIVATE_KEY,
			template_params: {
				name,
				email,
				message
			}
		};

		try {
			const response = await fetch('https://api.emailjs.com/api/v1.0/email/send', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(data)
			});

			if (response.ok) {
				return { success: true };
			} else {
				const errorText = await response.text();
				console.error('EmailJS API Error:', errorText);
				return fail(response.status, {
					error: `Помилка відправки: ${errorText}`,
					name,
					email,
					message
				});
			}
		} catch (error) {
			console.error('Fetch Error:', error);
			return fail(500, {
				error: 'Не вдалося підключитися до сервісу відправки.',
				name,
				email,
				message
			});
		}
	}
};
