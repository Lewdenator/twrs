use crossterm::{
    event::{self, KeyCode, KeyEvent},
    execute,
    terminal::{self, ClearType, EnterAlternateScreen, LeaveAlternateScreen},
    cursor::{self, MoveTo},
};
use std::io::{self, Write};
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    let height = 12;
    let width = 10;
    let grid = vec![vec![0; width]; height];
    let mut x = 0;
    let mut y = 0;

    terminal::enable_raw_mode()?;
    execute!(
        io::stdout(),
        EnterAlternateScreen,
        cursor::Hide
    )?;

    loop {
        execute!(
            io::stdout(),
            terminal::Clear(ClearType::All),
            MoveTo(0, 0)
        )?;

        for (i, row) in grid.iter().enumerate() {
            for (j, &val) in row.iter().enumerate() {
                if i == y && j == x {
                    print!("X ");
                } else {
                    print!("{} ", val);
                }
            }
            print!("\r\n");
        }

        io::stdout().flush()?;

        if let event::Event::Key(KeyEvent { code, .. }) = event::read()? {
            match code {
                KeyCode::Up if y > 0 => y -= 1,
                KeyCode::Down if y < height - 1 => y += 1,
                KeyCode::Left if x > 0 => x -= 1,
                KeyCode::Right if x < width - 1 => x += 1,
                KeyCode::Esc => break,
                _ => {}
            }
        }
    }

    execute!(
        io::stdout(),
        LeaveAlternateScreen,
        cursor::Show
    )?;
    terminal::disable_raw_mode()?;

    Ok(())
}
