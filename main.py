import interactions
from interactions import slash_command, listen, Client, SlashContext, ActionRow, Button, ButtonStyle, Task, IntervalTrigger, PartialEmoji


import logging
logging.basicConfig()
cls_log = logging.getLogger('MyLogger')
cls_log.setLevel(logging.DEBUG)

client = Client(intents=interactions.Intents.ALL, token='', sync_interactions=True, asyncio_debug=True, logger=cls_log, send_command_tracebacks=False)


@listen()
async def on_startup():
    print(f'{client.user} connected to discord')


from tetris_game_logic import TetrisGame, GameOver

game = TetrisGame()


@Task.create(IntervalTrigger(seconds=1))
async def game_task(ctx, message):
    try:
        game.tick()
        embed_color = 0xFFFFFF if game.cleared_line else None
        game_field = interactions.EmbedField(
            name=f'score: {game.score}',
            value=game.draw(),
            inline= True
        )
        hold_field = interactions.EmbedField(
            name='holding',
            value=game.get_held_block_visual(),
            inline=True
        )
        embed = interactions.Embed(fields=[game_field, hold_field], color=embed_color)
        await message.edit(embed=embed.to_dict())
    except GameOver:
        game_task.stop()
        game_field = interactions.EmbedField(
            name=f'game over | score: {game.score}',
            value=game.draw(),
            inline= True
        )
        hold_field = interactions.EmbedField(
            name='holding',
            value=game.get_held_block_visual(),
            inline=True
        )
        embed = interactions.Embed(fields=[game_field, hold_field])
        await message.edit(embed=embed.to_dict(), components=[])
        game.__init__()


@slash_command(name='tetris', description='start a game of tetris')
async def start(ctx: SlashContext):
    tetrisbuttons = [
        ActionRow(
            Button(
                style=ButtonStyle.BLURPLE,
                emoji=PartialEmoji.from_str(':left_right_arrow:'),
                custom_id='hold'
            ),
            Button(
                style=ButtonStyle.BLURPLE,
                emoji=PartialEmoji.from_str(':arrows_counterclockwise:'),
                custom_id='rotate'
            ),
            Button(
                style=ButtonStyle.DANGER,
                emoji=PartialEmoji.from_str(':stop_button:'),
                custom_id='stop_tetris'
            )
        ),
        ActionRow(
            Button(
                style=ButtonStyle.BLURPLE,
                emoji=PartialEmoji.from_str(':arrow_left:'),
                custom_id="left",
            ),
            Button(
                style=ButtonStyle.BLURPLE,
                emoji=PartialEmoji.from_str(':arrow_down:'),
                custom_id='hard_drop'
            ),
            Button(
                style=ButtonStyle.BLURPLE,
                emoji=PartialEmoji.from_str(':arrow_right:'),
                custom_id='right'
            )
        )
    ]
    empty_hold_field = '\n'.join([':black_large_square:' * 4 for _ in range(4)])
    game_field = interactions.EmbedField(
        name='score: 0',
        value=game.draw(),
        inline=True
    )
    hold_field = interactions.EmbedField(
        name='holding',
        value= empty_hold_field,
        inline=True
    )
    embed = interactions.Embed(fields=[game_field, hold_field])
    embed_msg = await ctx.send(embed=embed.to_dict(), components=tetrisbuttons)
    game_task.start(ctx, embed_msg)


from interactions.api.events import Component


@listen()
async def on_component(event: Component):
    ctx = event.ctx
    match ctx.custom_id:
        case 'left':
            game.move("left")
            await ctx.send("", ephemeral=True)
        case 'right':
            game.move("right")
            await ctx.send("", ephemeral=True)
        case 'rotate':
            game.rotate()
            await ctx.send("", ephemeral=True)
        case 'hard_drop':
            game.hard_drop()
            await ctx.send("", ephemeral=True)
        case 'hold':
            game.swap_with_hold()
            await ctx.send("", ephemeral=True)
        case 'stop_tetris':
            game_task.stop()
            await ctx.send("", ephemeral=True)


client.start()
